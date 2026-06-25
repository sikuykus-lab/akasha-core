from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .config import Config


class Backend(Protocol):
    brain_path: Path

    def ensure_clone(self) -> None: ...

    def pull(self) -> None: ...

    def push(self) -> None: ...


@dataclass
class GithubBackend:
    """
    backend=github — brain живёт в private GitHub-репозитории (§2.5, §5).
    """

    brain_url: str
    local_root: Path = Path.home() / ".akash" / "github"

    @property
    def brain_path(self) -> Path:
        owner_repo = self.brain_url.rstrip("/").split("/")[-2:]
        path = self.local_root.joinpath(*owner_repo)
        return path

    def ensure_clone(self) -> None:
        if self.brain_path.exists():
            return
        self.brain_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", self.brain_url, str(self.brain_path)],
            check=True,
        )

    def pull(self) -> None:
        self.ensure_clone()
        subprocess.run(
            ["git", "pull", "--rebase", "--autostash"],
            check=True,
            cwd=self.brain_path,
        )

    def _commit_if_dirty(self, message: str = "AKASHA sync") -> None:
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.brain_path,
            capture_output=True,
            text=True,
            check=True,
        )
        if not status.stdout.strip():
            return
        subprocess.run(["git", "add", "-A"], cwd=self.brain_path, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=self.brain_path, check=True)

    def push(self) -> None:
        self.ensure_clone()
        self._commit_if_dirty()
        subprocess.run(
            ["git", "push"],
            check=True,
            cwd=self.brain_path,
        )


@dataclass
class ServerBackend:
    """
    backend=server — brain на сервере пользователя (§2.5, §15.1).

    Для v1 реализуем два сценария:
    - агент уже на сервере → brain_path локальный каталог с git-репозиторием;
    - удалённый сервер → ssh/rsync, если указан brain_host.
    """

    brain_path: Path
    brain_host: str | None = None

    def ensure_clone(self) -> None:
        # Для server-backend считаем, что каталог уже создан по договорённости с пользователем.
        self.brain_path.mkdir(parents=True, exist_ok=True)

    def pull(self) -> None:
        self.ensure_clone()
        if self.brain_host:
            # Упрощённый вариант: подтягиваем изменения через git по SSH.
            subprocess.run(
                ["ssh", self.brain_host, "cd", str(self.brain_path), "&&", "git", "pull", "--rebase"],
                check=True,
            )
        else:
            subprocess.run(
                ["git", "pull", "--rebase"],
                check=True,
                cwd=self.brain_path,
            )

    def push(self) -> None:
        self.ensure_clone()
        if self.brain_host:
            subprocess.run(
                ["ssh", self.brain_host, "cd", str(self.brain_path), "&&", "git", "push"],
                check=True,
            )
        else:
            subprocess.run(
                ["git", "push"],
                check=True,
                cwd=self.brain_path,
            )


def load_backend(cfg: Config) -> Backend:
    """
    Выбор backend по config.local (§2.5).
    """
    if cfg.backend == "github":
        if not cfg.brain_url:
            raise SystemExit("config.local: backend=github, но не указан brain_url")
        backend: Backend = GithubBackend(brain_url=cfg.brain_url)
        backend.ensure_clone()
        return backend

    if cfg.backend == "server":
        if not cfg.brain_path:
            raise SystemExit("config.local: backend=server, но не указан brain_path")
        brain_path = Path(os.path.expanduser(cfg.brain_path))
        backend = ServerBackend(brain_path=brain_path, brain_host=cfg.brain_host)
        backend.ensure_clone()
        return backend

    raise SystemExit("config.local: backend is not configured (expected 'github' or 'server')")


def cli_backend_detect() -> None:
    """
    Простейшая проверка доступности GitHub/сервера (§3.2, §11).
    """
    available: list[str] = []
    # GitHub: считаем доступным, если установлен git и настроен gh / SSH (проверяем git версию как минимальный сигнал).
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        available.append("github")
    except Exception:
        pass

    # server: ориентируемся на наличие SSH-клиента.
    try:
        subprocess.run(["ssh", "-V"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        available.append("server")
    except Exception:
        pass

    if not available:
        print("No backend detected (github/server unavailable)", file=sys.stderr)  # type: ignore[name-defined]
    else:
        print("Available backends:", ", ".join(sorted(available)))


def cli_github_status() -> None:
    """
    Обёртка вокруг `gh auth status`, если gh доступен.
    """
    try:
        subprocess.run(["gh", "auth", "status"], check=False)
    except FileNotFoundError:
        print("gh CLI not found; install GitHub CLI to use github-status")

