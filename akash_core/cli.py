import argparse
import sys
from pathlib import Path

from . import config as config_mod
from . import backend as backend_mod
from . import brain as brain_mod
from . import session as session_mod
from . import nav as nav_mod
from . import harvest as harvest_mod
from . import upp as upp_mod
from . import onboard as onboard_mod
from .cli_resolve import ensure_akasha_core_installed


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="akash", description="AKASHA core CLI (akash-core v1).")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # adopt / adopt --server
    adopt = subparsers.add_parser("adopt", help="Bootstrap AKASHA on this machine / agent.")
    adopt.add_argument("brain", help="GitHub URL of brain repo or server spec, depending on mode.")
    adopt.add_argument("--agent", dest="agent_id", required=True, help="Platform/agent id (e.g. cursor, hermes).")
    adopt.add_argument(
        "--server",
        action="store_true",
        help="Treat 'brain' argument as server backend spec (user@host:PATH).",
    )

    subparsers.add_parser("backend-detect", help="Detect available backend(s): github and/or server.")
    subparsers.add_parser("github-status", help="Check GitHub auth status for akasha-core.")

    onboard = subparsers.add_parser(
        "onboard",
        help="Full auto-bootstrap: SaaS install → your private brain → shell → harvest → sync.",
    )
    onboard.add_argument(
        "brain",
        nargs="?",
        default=None,
        help="akasha-core (SaaS) URL, your akash-brain URL, or omit to auto-create private brain.",
    )
    onboard.add_argument("--agent", dest="agent_id", default="cursor")
    onboard.add_argument("--scope", choices=["project", "user"], default="project")
    onboard.add_argument("--skip-harvest", action="store_true")

    create_brain = subparsers.add_parser(
        "create-brain",
        help="Create private akash-brain on the authenticated user's GitHub.",
    )
    create_brain.add_argument("--name", default="akash-brain")

    subparsers.add_parser("doctor", help="Diagnose CLI, config, brain, GitHub.")
    subparsers.add_parser("ensure-cli", help="Install akasha-core if missing; write ~/.akash/cli.json.")

    subparsers.add_parser("init", help="Initialize a new brain repository in the current directory.")
    subparsers.add_parser("migrate", help="Migrate existing brain repository to latest manifest/layout.")

    configure = subparsers.add_parser("configure", help="Configure ~/.akash/config.local.")
    configure.add_argument("--backend", choices=["github", "server"], required=True)
    configure.add_argument("--brain-url", help="GitHub brain repository URL.")
    configure.add_argument("--brain-host", help="Server host spec user@host[:port].")
    configure.add_argument("--brain-path", help="Brain path on server (for backend=server).")
    configure.add_argument("--agent-id", required=True, help="Agent id, e.g. cursor, hermes.")
    configure.add_argument("--scope", choices=["project", "user"], required=True)

    subparsers.add_parser("pull", help="Start session: pull brain and hot memory.")
    prepare = subparsers.add_parser("prepare", help="Weave pack for a new task.")
    prepare.add_argument("task", help="Task description for prepare().")

    read_skill = subparsers.add_parser("read-skill", help="Read a skill fragment from current pack.")
    read_skill.add_argument("skill_id", help="Skill identifier.")

    remember = subparsers.add_parser("remember", help="Record facts during session.")
    remember.add_argument("fact", help="Single fact to remember.")

    record_outcome = subparsers.add_parser("record-outcome", help="Record skill usage outcome.")
    record_outcome.add_argument("skill_id")
    record_outcome.add_argument("outcome", choices=["success", "failure"])
    record_outcome.add_argument("--help-score", type=int, default=1)

    subparsers.add_parser("compact-check", help="Check if hot memory needs compaction.")
    subparsers.add_parser("sync", help="Sync brain: pull, compact, NAV, push.")

    harvest = subparsers.add_parser("harvest", help="Harvest from current aggregator into brain.")
    harvest.add_argument("--preview", action="store_true", help="Preview harvest without writing.")
    harvest.add_argument("--merge", action="store_true", help="Merge-only mode for repeated bootstrap.")

    subparsers.add_parser("import-legacy", help="Import legacy SOUL/USER/MEMORY and skills into brain.")

    export_session = subparsers.add_parser("export-session", help="Export UPP session block.")
    export_session.add_argument("--agent", required=True)

    export_pack = subparsers.add_parser("export-pack", help="Export UPP pack block for a task.")
    export_pack.add_argument("task")
    export_pack.add_argument("--agent", required=True)

    ingest_session = subparsers.add_parser("ingest-session", help="Ingest AKASHA-INGEST block from stdin.")
    ingest_session.add_argument("--agent", required=True)

    subparsers.add_parser("status", help="Show brain status and config.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "ensure-cli":
        ensure_akasha_core_installed()
        print("akasha-core ready.")
        return 0

    if args.command == "doctor":
        return onboard_mod.cli_doctor()

    if args.command == "onboard":
        return onboard_mod.cli_onboard(
            brain_url=args.brain,
            agent_id=args.agent_id,
            scope=args.scope,
            skip_harvest=args.skip_harvest,
        )

    if args.command == "create-brain":
        from .github_brain import ensure_user_brain_repo

        url = ensure_user_brain_repo(args.name)
        print(url)
        return 0

    config = config_mod.load_config()

    if args.command == "adopt":
        ensure_akasha_core_installed()
        if args.server:
            config_mod.configure_server_backend(
                agent_id=args.agent_id,
                server_spec=args.brain,
            )
        else:
            config_mod.configure_github_backend(
                agent_id=args.agent_id,
                brain_url=args.brain,
            )
        backend = backend_mod.load_backend(config_mod.load_config())
        brain_mod.bootstrap_brain(backend, agent_id=args.agent_id)
        return 0

    if args.command == "backend-detect":
        backend_mod.cli_backend_detect()
        return 0

    if args.command == "github-status":
        backend_mod.cli_github_status()
        return 0

    if args.command == "init":
        brain_mod.init_brain(Path.cwd())
        return 0

    if args.command == "migrate":
        brain_mod.migrate_brain(Path.cwd())
        return 0

    if args.command == "configure":
        config_mod.write_config(
            config_mod.Config(
                backend=args.backend,
                brain_url=args.brain_url,
                brain_host=args.brain_host,
                brain_path=args.brain_path,
                agent_id=args.agent_id,
                scope=args.scope,
            )
        )
        return 0

    backend = backend_mod.load_backend(config)

    if args.command == "pull":
        brain_mod.pull_brain(backend)
        session_mod.load_hot_memory(backend.brain_path)
        return 0

    if args.command == "prepare":
        nav_mod.cli_prepare(backend, args.task)
        return 0

    if args.command == "read-skill":
        nav_mod.cli_read_skill(backend, args.skill_id)
        return 0

    if args.command == "remember":
        session_mod.cli_remember(args.fact)
        return 0

    if args.command == "record-outcome":
        session_mod.cli_record_outcome(
            skill_id=args.skill_id,
            outcome=args.outcome,
            help_score=args.help_score,
        )
        return 0

    if args.command == "compact-check":
        session_mod.cli_compact_check(backend.brain_path)
        return 0

    if args.command == "sync":
        brain_mod.cli_sync(backend)
        return 0

    if args.command == "harvest":
        harvest_mod.cli_harvest(backend, preview=args.preview, merge=args.merge)
        return 0

    if args.command == "import-legacy":
        harvest_mod.cli_import_legacy(backend)
        return 0

    if args.command == "export-session":
        upp_mod.cli_export_session(agent=args.agent)
        return 0

    if args.command == "export-pack":
        upp_mod.cli_export_pack(agent=args.agent, task=args.task)
        return 0

    if args.command == "ingest-session":
        upp_mod.cli_ingest_session(agent=args.agent, stdin=sys.stdin.read())
        return 0

    if args.command == "status":
        brain_mod.cli_status(backend, config)
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

