AKASHA Core — instructions (EN)
================================

Short guide to `akasha-core`. **Full command reference** — [README.en.md](../README.en.md).

## 1. Prerequisites

- Python 3.11+
- `git`; for GitHub — `gh auth login` or SSH
- Install:

```bash
python3 -m pip install --user git+https://github.com/sikuykus-lab/akasha-core.git
```

## 2. Bootstrap (recommended)

Chat phrase:

> **Set yourself up from this GitHub project:** `https://github.com/sikuykus-lab/akasha-core`

Terminal:

```bash
python3 -m akash_core.cli onboard https://github.com/sikuykus-lab/akasha-core --agent cursor
```

After onboard: `~/.akash/config.local`, brain clone at `~/.akash/github/<user>/akash-brain`.

Agent checklist: `docs/AGENT-ONBOARDING.en.md`.

## 3. Existing brain

```bash
akash adopt https://github.com/<user>/akash-brain --agent cursor
```

## 4. Server brain

```bash
akash adopt --server user@host:~/.akash/brain --agent hermes
```

## 5. Lifecycle

```bash
akash pull
akash prepare "task description"
akash read-skill <skill_id>
akash remember "fact"
akash record-outcome <skill_id> success
akash sync
```

## 6. Diagnostics

```bash
akash doctor
akash status
akash install-shell   # after core upgrade
```
