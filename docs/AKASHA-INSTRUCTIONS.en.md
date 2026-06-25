AKASHA Core — Instructions (EN)
===============================

This document explains how to connect and use AKASHA Core (`akasha-core`)
according to `AKASHA-TZ v1.8`.

1. Prerequisites
----------------

- Python 3.11+ installed.
- `git` installed and GitHub auth configured (for GitHub backend).
- `akasha-core` installed:

```bash
pip install git+https://github.com/sikuykus-lab/akasha-core.git
```

2. Option A — brain in a private GitHub repository
--------------------------------------------------

1. Create or choose a **private** AKASHA brain repository, for example:

   - `https://github.com/<user>/akash-brain`

2. On the machine/agent where `akasha-core` is installed, run bootstrap:

   - In a terminal:

     ```bash
     akash adopt https://github.com/<user>/akash-brain --agent cursor
     ```

   - Or by telling your code agent (Cursor, Claude Code, etc.):

     > Set yourself up from this GitHub project: `https://github.com/<user>/akash-brain`

3. After bootstrap:

   - `~/.akash/config.local` contains `backend: github` and `brain_url`.
   - A local clone of the brain repo is stored under `~/.akash/github/<owner>/<repo>`.

3. Option B — brain on your own server
--------------------------------------

1. On the server, create a directory for the brain, e.g.:

   - `~/.akash/brain`

2. If the agent already runs **on** the server (Hermes over SSH, etc.):

   - Run:

     ```bash
     akash adopt --server user@host:~/.akash/brain --agent hermes
     ```

   - Or in chat:

     > Use my server instead of GitHub for the AKASHA brain — `ssh user@host`, brain in `~/.akash/brain`

3. For a remote brain via SSH:

   - `~/.akash/config.local` will have `backend: server`, `brain_host` and `brain_path`.

4. Core CLI commands
--------------------

All commands are specified in §11 of `AKASHA-TZ v1.8`. Short list:

- `akash backend-detect` — detect available backends (`github` / `server`).
- `akash init` — initialize a brain repository structure in the current directory.
- `akash migrate` — migrate an existing brain to the current layout.
- `akash configure` — manual edit of `~/.akash/config.local` (backend, brain_url/brain_host, scope).
- `akash pull` — start of a session: `pull` brain + load hot memory (`persona`, `rapport`, `ACTIONS`).
- `akash prepare "task description"` — weave a skill pack for a new task.
- `akash read-skill <skill_id>` — read `SKILL.md` from the current pack.
- `akash remember "fact"` — write a fact to the session buffer.
- `akash record-outcome <skill_id> <success|failure> [--help-score N]` — record skill usage outcome.
- `akash compact-check` — check if hot memory needs compaction.
- `akash sync` — `pull → compact → NAV → push` brain.
- `akash harvest [--preview] [--merge]` — run harvest based on adapters.
- `akash import-legacy` — narrow harvest mode for SOUL/USER/MEMORY/AGENTS.
- `akash export-session` / `akash export-pack` / `akash ingest-session` — UPP transport for agents without tools.
- `akash status` — show current `brain_version`, backend and basic info.

5. Typical session lifecycle
----------------------------

1. A new chat starts in the agent → lifecycle hook calls:

   ```bash
   akash pull
   ```

2. For a new task, the agent calls:

   ```bash
   akash prepare "task description"
   akash read-skill <skill_id>   # as needed
   ```

3. While working:

   ```bash
   akash remember "fact about user/task"
   akash record-outcome <skill_id> success --help-score 1
   ```

4. Periodically and at the end of the session:

   ```bash
   akash sync
   ```

