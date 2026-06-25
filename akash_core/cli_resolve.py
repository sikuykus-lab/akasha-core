from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

AKASHA_CORE_REPO = "git+https://github.com/sikuykus-lab/akasha-core.git"
CLI_MANIFEST = Path.home() / ".akash" / "cli.json"


def cli_invocation() -> list[str]:
    """
    Команда для subprocess и hooks — работает без akash в PATH.
    """
    return [sys.executable, "-m", "akash_core.cli"]


def cli_command_string(subcommand: str) -> str:
    """Строка для hooks.json: `python3 -m akash_core.cli pull`."""
    return " ".join([*cli_invocation(), subcommand])


def akash_in_path() -> str | None:
    return shutil.which("akash")


def save_cli_manifest() -> None:
    CLI_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "invocation": cli_invocation(),
        "command_prefix": " ".join(cli_invocation()),
        "akash_in_path": akash_in_path(),
        "python": sys.executable,
    }
    CLI_MANIFEST.write_text(json.dumps(data, indent=2), encoding="utf-8")


def ensure_akasha_core_installed(*, quiet: bool = False) -> None:
    """
    Установить akasha-core, если пакет недоступен. Агент вызывает сам при bootstrap.
    """
    try:
        import akash_core  # noqa: F401
        save_cli_manifest()
        return
    except ImportError:
        pass

    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--user",
        AKASHA_CORE_REPO,
    ]
    if not quiet:
        print("Installing akasha-core...", file=sys.stderr)
    subprocess.run(cmd, check=True)
    save_cli_manifest()

    if not akash_in_path() and not quiet:
        print(
            "Note: `akash` may not be in PATH; hooks use "
            f"`{' '.join(cli_invocation())}` instead.",
            file=sys.stderr,
        )
