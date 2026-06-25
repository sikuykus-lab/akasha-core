---
description: AKASHA — сначала паутина (помощь, не блокировка)
alwaysApply: true
---

# AKASHA lifecycle

Brain: `~/.akash/config.local`.

Кубик = **кусок под ситуацию** (функция, файл, паттерн), не готовое решение.  
`prepare` собирает **наводку на сборку** — какие entrypoints склеить, в каком порядке.

## На каждую новую задачу

1. `pull` — sessionStart hook
2. `prepare "<задача>"` → weave: hint + assembly + кубики (сколько нужно)
3. `read-skill <id>` — якорь и glue из assembly
4. **Собери** новое из entrypoints; не копируй skill целиком
5. Нет кубиков → с нуля
6. Успех → `create-skill` / `record-outcome` + `sync`

**Не блокировка** — наводка на сборку, не запрет на инструменты.

## Hooks

- `sessionStart` → pull + контекст brain
- `stop` → sync
