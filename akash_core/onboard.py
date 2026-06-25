from __future__ import annotations

import sys
from pathlib import Path

from . import backend as backend_mod
from . import brain as brain_mod
from . import config as config_mod
from . import harvest as harvest_mod
from .adapter import detect_project_root, install_cursor_shell
from .cli_resolve import ensure_akasha_core_installed
from .github_brain import initial_push_if_needed, resolve_brain_url

AKASHA_CORE_SAAS = "https://github.com/sikuykus-lab/akasha-core"


def cli_onboard(
    *,
    brain_url: str | None,
    agent_id: str,
    scope: str = "project",
    project_root: Path | None = None,
    skip_harvest: bool = False,
) -> int:
    """
    Полный bootstrap (§3.1): SaaS akasha-core → private brain на GitHub пользователя → shell → harvest → sync.
    """
    ensure_akasha_core_installed()
    project_root = detect_project_root(project_root)

    backend_mod.cli_backend_detect()

    resolved_brain = resolve_brain_url(brain_url)
    config_mod.configure_github_backend(agent_id=agent_id, brain_url=resolved_brain)
    cfg = config_mod.load_config()
    cfg.scope = scope  # type: ignore[assignment]
    config_mod.write_config(cfg)

    backend = backend_mod.load_backend(config_mod.load_config())
    brain_mod.bootstrap_brain(backend, agent_id=agent_id)
    initial_push_if_needed(backend.brain_path)

    shell_files = install_cursor_shell(
        brain_path=backend.brain_path,
        project_root=project_root,
        agent_id=agent_id,
    )

    merge = (backend.brain_path / "memory" / "ACTIONS.md").stat().st_size > 0 if (
        backend.brain_path / "memory" / "ACTIONS.md"
    ).exists() else False

    if not skip_harvest:
        harvest_mod.run_harvest(backend, preview=True, merge=merge, project_root=project_root)
        harvest_mod.run_harvest(backend, preview=False, merge=merge, project_root=project_root)

    brain_mod.pull_brain(backend)
    brain_mod.cli_sync(backend)

    manifest = brain_mod._read_manifest(backend.brain_path / brain_mod.MANIFEST_NAME)
    skill_count = harvest_mod.count_skills(backend.brain_path)

    print("\n**Готов к работе. Мы — есть AKASHA.**")
    print(f"Brain v{manifest.brain_version} · {agent_id} · cli · github · {resolved_brain}")
    print(f"SaaS core: {AKASHA_CORE_SAAS}")
    print(f"Skills: {skill_count}")
    print(f"Scope: {scope}")
    print(f"Clone: {backend.brain_path}")
    print("Shell:", ", ".join(shell_files))
    print("Hooks use:", f"python -m akash_core.cli (no PATH required)")
    return 0


def cli_doctor() -> int:
    """Диагностика: CLI, config, brain, GitHub."""
    from .cli_resolve import CLI_MANIFEST, akash_in_path, cli_invocation

    print("=== AKASHA doctor ===")
    try:
        import akash_core

        print(f"package: ok ({akash_core.__file__})")
    except ImportError:
        print("package: MISSING — run onboard or pip install akasha-core")
        return 1

    print(f"python: {sys.executable}")
    print(f"akash in PATH: {akash_in_path() or 'no (use python -m akash_core.cli)'}")
    print(f"cli invocation: {' '.join(cli_invocation())}")
    print(f"manifest: {CLI_MANIFEST} ({'exists' if CLI_MANIFEST.exists() else 'missing'})")

    cfg = config_mod.load_config()
    if not cfg.backend:
        print("config: not configured — run onboard")
        return 1
    print(f"backend: {cfg.backend}")
    print(f"agent_id: {cfg.agent_id}")
    print(f"scope: {cfg.scope}")
    print(f"brain_url: {cfg.brain_url}")

    try:
        backend = backend_mod.load_backend(cfg)
        print(f"brain_path: {backend.brain_path} ({'exists' if backend.brain_path.exists() else 'MISSING'})")
        manifest = brain_mod._read_manifest(backend.brain_path / brain_mod.MANIFEST_NAME)
        print(f"brain_version: {manifest.brain_version}")
        print(f"skills: {harvest_mod.count_skills(backend.brain_path)}")
    except SystemExit as e:
        print(f"brain: error — {e}")
        return 1

    backend_mod.cli_backend_detect()
    return 0
