# akasha-bootstrap

Первый skill, который читает агрегатор при bootstrap (§12 AKASHA-TZ v1.8).

## Когда срабатывает

Пользователь написал одну из фраз:

- «Настрой себя по данному проекту GitHub: `<URL>`»
- «подключи мозг AKASHA» / «настрой AKASHA»

## Что делать (по порядку)

1. Определи `agent_id` платформы → `adapters/<platform>/`.
2. Установи и запусти onboard (PATH не нужен):

```bash
python3 -m pip install --user --upgrade git+https://github.com/sikuykus-lab/akasha-core.git
python3 -m akash_core.cli onboard <BRAIN_URL> --agent <agent_id> --scope project
python3 -m akash_core.cli doctor
```

3. Если onboard уже выполнен — прочитай `adapters/<platform>/bootstrap.md` для проверки.
4. Финальное сообщение §3.1.

## MUST после установки

- `sessionStart` → `python3 -m akash_core.cli pull`
- новая задача → `akash prepare` → `read-skill` только из pack
- факты → `akash remember`
- конец → `akash sync`
- **не читать** `skills/` целиком

## Ссылка на полный чеклист агента

https://github.com/sikuykus-lab/akasha-core/blob/main/docs/AGENT-ONBOARDING.ru.md
