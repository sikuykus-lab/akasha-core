---
description: AKASHA lifecycle — паутина skills (без блокировки инструментов)
alwaysApply: true
---

# AKASHA lifecycle

Brain: `~/.akash/config.local`. **Инструменты не блокируются.**

## На задачу (рекомендуется)

1. `pull` — sessionStart hook
2. `prepare "<задача>"` — lego-кубики из NAV
3. `read-skill` из pack, если есть
4. Работа (можно с нуля)
5. После успеха — skill в brain + `record-outcome` + `sync`

Skills — через `prepare` / `read-skill`, не каталог `skills/` целиком.

## Hooks

- `sessionStart` → pull + контекст
- `stop` → sync
- **preToolUse gate отключён** — агент не блокируется
