---
description: AKASHA lifecycle — автоподключение к паутине skills на каждую задачу
alwaysApply: true
---

# AKASHA lifecycle (MUST)

Ты работаешь через **AKASHA brain** (`~/.akash/config.local`). Это стандарт, не опция.

## Каждое сообщение пользователя с задачей

**Порядок строгий:**

1. `python3 -m akash_core.cli pull` — если новая сессия (hook уже делает на sessionStart)
2. `python3 -m akash_core.cli prepare "<текст задачи пользователя>"` — weave pack из NAV/паутины
3. `python3 -m akash_core.cli read-skill <id>` — **только** id из вывода prepare
4. Работа (код, файлы, инструменты)
5. `remember` / `record-outcome` по ходу; `sync` на stop hook

**Запрещено до шагов 2–3:** читать/править файлы проекта, искать по коду, предлагать решение без pack.

Исключение: вопрос «что такое…» без действий над репозиторием.

## Паутина skills (§7)

- Источник — **только** brain через `prepare` → `read-skill`
- **Не** читать `skills/` целиком, **не** @ все skills
- Lego-кубики в `NAV.yaml` → pack ≤ 5 skills на задачу

## Hooks

- `sessionStart` → pull + hot-память в контекст
- `preToolUse` → блок до prepare (разрешён только `akash_core.cli`)
- `stop` → sync
