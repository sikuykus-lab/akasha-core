# akasha-bootstrap

Первый skill, который читает агрегатор при bootstrap.

## Когда срабатывает

Пользователь написал одну из фраз:

- «Настрой себя по данному проекту GitHub: `https://github.com/sikuykus-lab/akasha-core`»
- «подключи мозг AKASHA» / «настрой AKASHA»

## Два репозитория

- **akasha-core** (публичный SaaS) — установка и документация
- **akash-brain** (private на GitHub **пользователя**) — память и skills

Не используй чужой private brain. Onboard сам создаст brain на профиле пользователя (`gh auth login` обязателен).

## Что делать (по порядку)

1. Определи `agent_id` платформы → `adapters/<platform>/`.
2. Установи и запусти onboard (PATH не нужен):

```bash
python3 -m pip install --user --upgrade git+https://github.com/sikuykus-lab/akasha-core.git
python3 -m akash_core.cli onboard https://github.com/sikuykus-lab/akasha-core --agent <agent_id> --scope project
python3 -m akash_core.cli doctor
```

3. Если onboard уже выполнен — прочитай `adapters/<platform>/bootstrap.md` для проверки.
4. Финальное сообщение пользователю (укажи URL **созданного** brain).

## После установки — сначала паутина

Перед работой по задаче — **сначала паутина** (помощь, не блокировка):

- `sessionStart` → `python3 -m akash_core.cli pull`
- новая задача → `prepare` → `read-skill` только из pack; нет кубиков — с нуля
- факты → `remember`; исход skill → `record-outcome`
- конец → `sync`
- **не читать** `skills/` целиком

## Ссылка на полный чеклист агента

https://github.com/sikuykus-lab/akasha-core/blob/main/docs/AGENT-ONBOARDING.ru.md
