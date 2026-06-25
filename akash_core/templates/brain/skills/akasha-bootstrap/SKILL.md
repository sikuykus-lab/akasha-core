# akasha-bootstrap

Первый skill, который читает агрегатор при bootstrap (§12 AKASHA-TZ v1.8).

## Когда срабатывает

Пользователь написал одну из фраз:

- «Настрой себя по данному проекту GitHub: `<URL>`»
- «подключи мозг AKASHA» / «настрой AKASHA»

## Что делать (по порядку)

1. Определи `agent_id` платформы → `adapters/<platform>/`.
2. Выполни `akash backend-detect`. Если GitHub доступен — `backend: github`.
3. `akash adopt <URL> --agent <agent_id>`
4. Прочитай `adapters/<platform>/bootstrap.md` и выполни чеклист.
5. Собери оболочку: `inject.md` → rule; `hooks.template.json` → hooks; `mcp.template.json` → MCP.
6. Спроси scope: `project` | `user`.
7. `akash harvest --preview` → подтверждение → `akash harvest` → `akash sync`
8. `akash pull` → финальное сообщение §3.1.

## MUST после установки

- `sessionStart` → `akash pull`
- новая задача → `akash prepare` → `read-skill` только из pack
- факты → `akash remember`
- конец → `akash sync`
- **не читать** `skills/` целиком

## Ссылка на полный чеклист агента

https://github.com/sikuykus-lab/akasha-core/blob/main/docs/AGENT-ONBOARDING.ru.md
