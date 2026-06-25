from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml


CONFIG_PATH = Path.home() / ".akash" / "config.local"

BackendKind = Literal["github", "server"]
ScopeKind = Literal["project", "user"]


@dataclass
class Config:
    backend: BackendKind | None = None
    brain_url: str | None = None
    brain_host: str | None = None
    brain_path: str | None = None
    agent_id: str | None = None
    scope: ScopeKind | None = None


def _ensure_config_dir() -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    """
    Load ~/.akash/config.local if it exists, otherwise return an empty Config.

    Формат файла соответствует §2.5 AKASHA-TZ (backend, brain_url/brain_host/brain_path, agent_id, scope).
    """
    if not CONFIG_PATH.exists():
        return Config()
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}
    return Config(
        backend=raw.get("backend"),
        brain_url=raw.get("brain_url"),
        brain_host=raw.get("brain_host"),
        brain_path=raw.get("brain_path"),
        agent_id=raw.get("agent_id"),
        scope=raw.get("scope"),
    )


def write_config(cfg: Config) -> None:
    """
    Persist config to ~/.akash/config.local.

    Секреты (tokens, SSH keys) сюда не пишем — они должны жить в env или внешних конфигах (§2.5, §14.7).
    """
    _ensure_config_dir()
    data: dict[str, Any] = {
        "backend": cfg.backend,
        "brain_url": cfg.brain_url,
        "brain_host": cfg.brain_host,
        "brain_path": cfg.brain_path,
        "agent_id": cfg.agent_id,
        "scope": cfg.scope,
    }
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def configure_github_backend(*, agent_id: str, brain_url: str) -> None:
    """
    Helper used by `akash adopt` в режиме GitHub-backend.
    """
    cfg = load_config()
    cfg.backend = "github"
    cfg.brain_url = brain_url
    cfg.brain_host = None
    cfg.brain_path = None
    cfg.agent_id = agent_id
    # scope выбирается позже через `akash configure`, здесь не навязываем.
    write_config(cfg)


def configure_server_backend(*, agent_id: str, server_spec: str) -> None:
    """
    Helper used by `akash adopt --server user@host:PATH`.

    server_spec формата `user@host:PATH` или `user@host[:port]:PATH`.
    """
    if ":" not in server_spec:
        raise SystemExit("server_spec must be user@host:PATH or user@host:port:PATH")
    host, brain_path = server_spec.split(":", 1)
    cfg = load_config()
    cfg.backend = "server"
    cfg.brain_host = host
    cfg.brain_path = brain_path
    cfg.brain_url = None
    cfg.agent_id = agent_id
    write_config(cfg)

