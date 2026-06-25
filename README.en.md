AKASHA Core (`akasha-core`)
===========================

Python core for **AKASHA** — shared memory and skills for AI agents (Cursor, Claude Code, Hermes, etc.).

- One **brain** (private GitHub or server directory) — persona, rapport, skills, NAV.
- CLI `akash` and library `akash_core`.
- Backends: `github` or `server`.
- **One-phrase** chat onboard — the agent installs the core and creates your private `akash-brain`.

**Translations:** [Русский](README.md) · [中文](README.zh.md)

## One phrase in chat

With GitHub configured (`gh auth login` or SSH):

> **Set yourself up from this GitHub project:** `https://github.com/sikuykus-lab/akasha-core`

The agent follows `docs/AGENT-ONBOARDING.en.md`. Also: `docs/AGENT-ONBOARDING.ru.md`, `docs/AGENT-ONBOARDING.zh.md`.

## Install

```bash
python3 -m pip install --user git+https://github.com/sikuykus-lab/akasha-core.git
```

From source (development):

```bash
cd akasha-core && pip install -e .
```

## Quick start

```bash
# full bootstrap: SaaS → your private brain → hooks → harvest
python3 -m akash_core.cli onboard https://github.com/sikuykus-lab/akasha-core --agent cursor

# brain already exists
akash adopt https://github.com/<your-user>/akash-brain --agent cursor

# brain on your server
akash adopt --server user@host:~/.akash/brain --agent hermes

akash status
akash pull
akash sync
```

## CLI commands

| Command | Purpose |
|---------|---------|
| `akash onboard [url]` | Full bootstrap: install → brain → shell → harvest → sync |
| `akash adopt <url>` | Connect existing brain (GitHub URL) |
| `akash adopt --server <user@host:path>` | Brain on user server |
| `akash create-brain` | Create private `akash-brain` on GitHub |
| `akash install-shell` | Reinstall Cursor hooks and rule after upgrade |
| `akash doctor` | Diagnose CLI, config, brain, GitHub |
| `akash ensure-cli` | Install `akasha-core` if missing |
| `akash backend-detect` | Available backends: `github` / `server` |
| `akash github-status` | GitHub auth status |
| `akash init` | Scaffold brain in current directory |
| `akash migrate` | Migrate brain to latest layout |
| `akash configure` | Edit `~/.akash/config.local` |
| `akash pull [--steal]` | Session start + **brain lock** (single writer) |
| `akash session-status` | Who holds the lock, TTL |
| `akash prepare "task"` | Weave skill pack for a task |
| `akash read-skill <id>` | Read SKILL.md from current pack |
| `akash remember "fact"` | Buffer a fact for the session |
| `akash record-outcome <id> success\|failure` | Record skill usage → usage.jsonl |
| `akash compact-check` | Check if hot memory needs compaction |
| `akash sync` | pull → compact → NAV → push to brain |
| `akash harvest [--preview] [--merge]` | Harvest from aggregator into brain |
| `akash import-legacy` | Narrow harvest: SOUL/USER/MEMORY/AGENTS |
| `akash export-session --agent <id>` | UPP: memory block for chat paste |
| `akash export-pack "task" --agent <id>` | UPP: pack for a task |
| `akash ingest-session --agent <id>` | UPP: parse AKASHA-INGEST block |
| `akash status` | brain_version, backend, scope |

MCP tools (when enabled) mirror the same operations.

## Parallel agents

Only **one session** may write to the brain at a time:

1. **Local** — file lock in `~/.akash/locks/` (two Cursor chats on one Mac).
2. **Cross-machine** — `state/session_lock.json` in brain (pushed on `pull`).

A second agent gets an error on `pull` / `sync` / `harvest`. Stale lock: `akash pull --steal` after TTL (10 min, renewed on `prepare` / `remember`).

## Session lifecycle

```
sessionStart  →  akash pull
new task      →  akash prepare "…"  →  akash read-skill <id>
work            →  akash remember  ·  akash record-outcome
end             →  akash sync
```

Read skills **only** via `prepare` / `read-skill` — not the whole `skills/` tree.

## Legal

`akasha-core` is **proprietary**, not open source. Rights: `sikuykus-lab`.

Allowed: integration with **your** private brain; AKASHA-compatible SaaS with owner approval.

- [LICENSE.md](LICENSE.md) — Russian (binding)
- [LICENSE.en.md](LICENSE.en.md) · [LICENSE.zh.md](LICENSE.zh.md) — translations

User guide: `docs/AKASHA-INSTRUCTIONS.en.md` (ru/zh in the same folder).
