---
description: AKASHA — сначала паутина (помощь, не блокировка)
alwaysApply: true
---

# AKASHA lifecycle

Brain: `~/.akash/config.local`.

Перед тем как копать проект вслепую — **сначала паутина**: есть ли уже lego-кубики под задачу?

## На каждую новую задачу

1. `pull` — sessionStart hook (hot-память)
2. `prepare "<задача>"` — NAV подберёт до 5 skills-кубиков
3. `read-skill <id>` — только то, что совпало с задачей
4. **Кубики подходят** → используй, быстрее к результату
5. **Нет подходящих / pack пуст** → работай с нуля, это нормально
6. После успеха → `remember`, `record-outcome`, `sync` (новый кубик в паутину)

**Не блокировка** — экономия времени, не запрет на инструменты.

Skills — через `prepare` / `read-skill`, не каталог `skills/` целиком.

## Hooks

- `sessionStart` → pull + контекст brain
- `stop` → sync
