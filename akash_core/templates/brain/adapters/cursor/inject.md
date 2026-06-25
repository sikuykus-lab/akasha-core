---
description: AKASHA lifecycle — pull, prepare, remember, sync
alwaysApply: true
---

# AKASHA lifecycle (MUST)

Старт сессии: выполни `akash pull` (hot-память: persona, rapport, ACTIONS).

Новая задача: `akash prepare "<задача>"` → читай skills **только** через `akash read-skill` из текущего pack.

В работе: `akash remember` для фактов; `akash record-outcome` при использовании skill.

Конец сессии / stop hook: `akash sync`.

**Запрещено:** читать каталог `skills/` целиком, @ все skills, копировать skills в проект. Источник — только brain через prepare.
