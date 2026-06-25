# akasha-create-skill-cli

tags: akasha, cli, create-skill, lego, brain
project: akasha-core

## Назначение
CLI create-skill — сохранить lego-кубик в brain после успешной задачи.

## Триггеры

- create-skill
- новый lego-кубик в brain
- сохранить skill после успешной задачи

## Шаги

1. Собери SKILL.md ≤4KB: заголовок, Триггеры, ≥2 шагов (Law I–III).
2. `python3 -m akash_core.cli create-skill <id> --project akasha-core --tags akasha cli` — тело из stdin или `--file`.
3. Опционально `--built-from id1 id2` для lego-связей.
4. `record-outcome <id> success` и `sync` — кубик в NAV и на GitHub.

## Paths

- `akash_core/skill_create.py`
- `akash_core/cli.py`

## Антипаттерны

- Не дублировать skill на тот же сценарий — merge или обнови существующий.
- Не класть в skill большие куски кода — только шаги и пути.
