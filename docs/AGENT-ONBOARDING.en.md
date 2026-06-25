# AKASHA — AI agent onboarding (EN)

**User trigger phrase (§3.1 AKASHA-TZ):**

> Set yourself up from this GitHub project: `https://github.com/<user>/akash-brain`

Russian equivalent: «Настрой себя по данному проекту GitHub: `<URL>`»

When you receive this phrase, **run the full checklist below yourself**. The user does not configure MCP, rules, or paths manually.

---

## Clean retest (wipe local install)

Before onboarding from GitHub, remove prior install:

```bash
rm -rf ~/.akash
rm -f .cursor/hooks.json .cursor/rules/akasha-lifecycle.mdc
python3 -m pip uninstall -y akasha-core
```

Optional: delete `https://github.com/<user>/akash-brain` on GitHub for an empty brain.

Install **only** from GitHub (`pip install git+...`), not `pip install -e` from a local clone.

---

## Bootstrap checklist (mandatory order)

### 0. Detect platform

`agent_id` = one of: `cursor` | `claude-code` | `hermes` | `opencode` | `_template`.

### 1. Install akasha-core (if `akash` is missing)

```bash
python3 -m pip install git+https://github.com/sikuykus-lab/akasha-core.git
```

Verify: `akash --help`

### 2. Check backend

```bash
akash backend-detect
akash github-status
```

If `github` is unavailable, stop and tell the user to connect GitHub (`gh auth login` or SSH key). Without storage, full AKASHA is not possible (§3.2).

### 3. Extract brain URL from the user message

Example: `https://github.com/sikuykus-lab/akash-brain`

### 4. Bootstrap

```bash
akash adopt <BRAIN_URL> --agent <agent_id>
```

This writes `~/.akash/config.local`, clones the brain, and scaffolds an empty repo.

### 5. Read instructions from the brain repo

After clone, open in the brain repository:

1. `skills/akash-bootstrap/SKILL.md` — main checklist (§12)
2. `adapters/<agent_id>/bootstrap.md` — platform steps
3. `adapters/<agent_id>/inject.md` — lifecycle rule text (MUST)
4. `adapters/<agent_id>/hooks.template.json` — sessionStart → pull, stop → sync
5. `adapters/<agent_id>/mcp.template.json` — if the platform uses MCP

If `adapters/<agent_id>/` is missing, use `adapters/_template/`.

### 6. Install local adapter shell

**Do not copy** skills or memory into the working project. Brain is the only source.

| Mechanism | Cursor (example) |
|-----------|------------------|
| Lifecycle rule | `.cursor/rules/akasha-lifecycle.mdc` with `alwaysApply: true` — from `inject.md` |
| Hooks | `.cursor/hooks.json` from `hooks.template.json` |
| MCP | `.cursor/mcp.json` entry from `mcp.template.json` |
| Config | `~/.akash/config.local` written by `adopt` |

Ask the user for **scope**: `project` or `user`. Then:

```bash
akash configure --backend github --brain-url <BRAIN_URL> --agent-id <agent_id> --scope project
```

### 7. Harvest

```bash
akash harvest --preview
```

Show the report. After user confirmation:

```bash
akash harvest
akash sync
```

For a second agent on the same brain: `akash harvest --merge`.

### 8. Verify

```bash
akash pull
akash status
```

### 9. Final message to the user (§3.1)

> **Ready. We are AKASHA.**  
> Brain vN · `<agent_id>` · `<transport>` · `github` · N skills (M imported at setup)  
> Profile and memory collected from your projects. Next agent: **same brain URL**.

---

## Post-bootstrap contract (every new chat)

```
sessionStart  → akash pull
new task      → akash prepare → read-skill (pack only)
work            → remember, record-outcome
end             → akash sync
```

**Forbidden:** reading all of `skills/` or @-mentioning every skill — use `prepare` / `read-skill` only.

---

## Links

- Core: https://github.com/sikuykus-lab/akasha-core
- Instructions: `docs/AKASHA-INSTRUCTIONS.en.md`
