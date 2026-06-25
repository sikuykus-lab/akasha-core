from __future__ import annotations

import fcntl
import hashlib
import json
import os
import socket
import subprocess
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

from .backend import Backend

LOCK_REL = Path("state") / "session_lock.json"
LOCAL_LOCKS_DIR = Path.home() / ".akash" / "locks"
LOCAL_TOKEN_FILE = Path.home() / ".akash" / "session_token.json"
DEFAULT_TTL_SEC = 600


@dataclass
class LockRecord:
    holder: str
    agent_id: str
    host: str
    pid: int
    token: str
    acquired_at: str
    renewed_at: str
    ttl_sec: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LockRecord | None:
        if not data or not data.get("token"):
            return None
        try:
            return cls(
                holder=str(data["holder"]),
                agent_id=str(data["agent_id"]),
                host=str(data["host"]),
                pid=int(data["pid"]),
                token=str(data["token"]),
                acquired_at=str(data["acquired_at"]),
                renewed_at=str(data["renewed_at"]),
                ttl_sec=int(data.get("ttl_sec", DEFAULT_TTL_SEC)),
            )
        except (KeyError, TypeError, ValueError):
            return None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def lock_path(brain_path: Path) -> Path:
    return brain_path / LOCK_REL


def _local_lock_file(brain_path: Path) -> Path:
    key = hashlib.sha256(str(brain_path.resolve()).encode("utf-8")).hexdigest()[:16]
    LOCAL_LOCKS_DIR.mkdir(parents=True, exist_ok=True)
    return LOCAL_LOCKS_DIR / f"{key}.lock"


@contextmanager
def local_exclusive(brain_path: Path) -> Iterator[None]:
    """Один writer на этой машине (два Cursor-чата, терминал + hook)."""
    path = _local_lock_file(brain_path)
    handle = path.open("w", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        handle.close()
        raise SystemExit(
            "AKASHA: на этой машине уже идёт сессия (другой агент или чат). "
            "Дождитесь `akash sync` или закройте второй агент."
        ) from exc
    try:
        handle.write(f"{os.getpid()}\n")
        handle.flush()
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def read_lock(brain_path: Path) -> LockRecord | None:
    path = lock_path(brain_path)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return LockRecord.from_dict(data)


def is_active(record: LockRecord, now: datetime | None = None) -> bool:
    now = now or _utc_now()
    renewed = _parse_iso(record.renewed_at)
    return (now - renewed).total_seconds() < record.ttl_sec


def expires_at(record: LockRecord) -> datetime:
    return _parse_iso(record.renewed_at) + timedelta(seconds=record.ttl_sec)


def load_local_token() -> dict[str, Any] | None:
    if not LOCAL_TOKEN_FILE.is_file():
        return None
    try:
        return json.loads(LOCAL_TOKEN_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def save_local_token(*, token: str, agent_id: str, brain_path: Path) -> None:
    LOCAL_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "token": token,
        "agent_id": agent_id,
        "brain_path": str(brain_path.resolve()),
        "pid": os.getpid(),
    }
    LOCAL_TOKEN_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def clear_local_token() -> None:
    LOCAL_TOKEN_FILE.unlink(missing_ok=True)


def _write_lock(brain_path: Path, record: LockRecord) -> None:
    path = lock_path(brain_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(record), ensure_ascii=False, indent=2), encoding="utf-8")


def _remove_lock(brain_path: Path) -> None:
    lock_path(brain_path).unlink(missing_ok=True)


def _commit_push_lock(backend: Backend, message: str) -> None:
    brain_path = backend.brain_path
    subprocess.run(["git", "add", str(LOCK_REL)], cwd=brain_path, check=True)
    status = subprocess.run(
        ["git", "status", "--porcelain", str(LOCK_REL)],
        cwd=brain_path,
        capture_output=True,
        text=True,
        check=True,
    )
    if not status.stdout.strip():
        return
    subprocess.run(["git", "commit", "-m", message], cwd=brain_path, check=True)
    push = subprocess.run(["git", "push"], cwd=brain_path, capture_output=True, text=True)
    if push.returncode != 0:
        subprocess.run(["git", "pull", "--rebase", "--autostash"], cwd=brain_path, check=True)
        push = subprocess.run(["git", "push"], cwd=brain_path, capture_output=True, text=True)
        if push.returncode != 0:
            raise SystemExit(
                "AKASHA: не удалось опубликовать блокировку сессии (другой агент пишет в brain). "
                "Повторите `akash pull` через несколько секунд."
            )


def _new_record(agent_id: str, token: str, ttl_sec: int) -> LockRecord:
    now = _iso(_utc_now())
    host = socket.gethostname()
    holder = f"{agent_id}@{host}:{os.getpid()}"
    return LockRecord(
        holder=holder,
        agent_id=agent_id,
        host=host,
        pid=os.getpid(),
        token=token,
        acquired_at=now,
        renewed_at=now,
        ttl_sec=ttl_sec,
    )


def acquire(backend: Backend, agent_id: str, *, steal: bool = False, ttl_sec: int = DEFAULT_TTL_SEC) -> str:
    """
    Эксклюзивная сессия: локальный fcntl + lease в brain (push).
    """
    brain_path = backend.brain_path
    with local_exclusive(brain_path):
        backend.pull()
        existing = read_lock(brain_path)
        local = load_local_token()
        now = _utc_now()

        if existing and is_active(existing, now):
            if local and local.get("token") == existing.token:
                existing.renewed_at = _iso(now)
                _write_lock(brain_path, existing)
                save_local_token(token=existing.token, agent_id=agent_id, brain_path=brain_path)
                return existing.token
            if not steal:
                until = expires_at(existing).strftime("%H:%M UTC")
                raise SystemExit(
                    f"AKASHA: brain занят — {existing.agent_id} на {existing.host} "
                    f"(активен до ~{until}). "
                    "Дождитесь `akash sync` у того агента или `akash pull --steal`, если сессия зависла."
                )

        token = str(uuid.uuid4())
        record = _new_record(agent_id, token, ttl_sec)
        _write_lock(brain_path, record)
        save_local_token(token=token, agent_id=agent_id, brain_path=brain_path)
        _commit_push_lock(backend, "AKASHA session lock")
        return token


def renew(backend: Backend, agent_id: str) -> None:
    """Продлить lease (prepare / remember / record-outcome)."""
    local = load_local_token()
    if not local or local.get("agent_id") != agent_id:
        return
    brain_path = backend.brain_path
    if str(brain_path.resolve()) != str(local.get("brain_path", "")):
        return
    record = read_lock(brain_path)
    if not record or record.token != local.get("token"):
        return
    if not is_active(record):
        return
    record.renewed_at = _iso(_utc_now())
    _write_lock(brain_path, record)


def release(backend: Backend, agent_id: str) -> None:
    """Снять lease (удаление файла попадёт в общий commit при sync)."""
    brain_path = backend.brain_path
    local = load_local_token()
    record = read_lock(brain_path)
    if record and local and record.token == local.get("token"):
        _remove_lock(brain_path)
        subprocess.run(["git", "add", str(LOCK_REL)], cwd=brain_path, check=True)
    clear_local_token()


def assert_holder(backend: Backend, agent_id: str) -> None:
    """Перед sync/harvest — только владелец lease может писать в brain."""
    local = load_local_token()
    if not local:
        raise SystemExit("AKASHA: нет активной сессии. Сначала `akash pull`.")
    if local.get("agent_id") != agent_id:
        raise SystemExit("AKASHA: токен сессии не совпадает с текущим agent_id.")
    record = read_lock(backend.brain_path)
    if not record or not is_active(record):
        raise SystemExit("AKASHA: lease истёк. Выполните `akash pull` заново.")
    if record.token != local.get("token"):
        holder = f"{record.agent_id}@{record.host}"
        raise SystemExit(
            f"AKASHA: brain пишет другой агент ({holder}). "
            "Дождитесь его sync или `akash pull --steal` после истечения TTL."
        )


def cli_session_status(backend: Backend, agent_id: str | None) -> None:
    backend.pull()
    record = read_lock(backend.brain_path)
    local = load_local_token()
    print("=== AKASHA session lock ===")
    if not record:
        print("Lock: free")
        return
    active = is_active(record)
    print(f"Holder: {record.holder}")
    print(f"Agent: {record.agent_id}")
    print(f"Active: {'yes' if active else 'stale'}")
    if active:
        print(f"Expires ~: {expires_at(record).isoformat()}")
    if local:
        mine = local.get("token") == record.token
        print(f"This machine holds lock: {'yes' if mine else 'no'}")
    if agent_id:
        print(f"Configured agent_id: {agent_id}")
