AKASHA Core (`akasha-core`)
===========================

Это Python-реализация ядра AKASHA (`akash-core v1`) строго по документу `AKASHA-TZ v1.8`.

- Один brain-репозиторий (GitHub private или каталог на сервере) с фиксированной структурой.
- CLI `akash` и библиотека `akash_core` для операций `adopt`, `pull`, `prepare`, `remember`, `sync` и др.
- Поддержка backend'ов `github` и `server` как в разделе §2.5 ТЗ.

Единственный источник правды по поведению — файл ТЗ:

- `AKASHA-TZ v1.8` (копия в рабочем репозитории пользователя, например `Google Sheets/akash/AKASHA-TZ.md`).

## Для пользователя: одна фраза в чат

Если на устройстве подключён GitHub (`gh auth login` или SSH), напишите агрегатору:

> **Настрой себя по данному проекту GitHub:** `https://github.com/sikuykus-lab/akasha-core`

ИИ **сам** установит `akasha-core`, создаст **ваш** private `akash-brain` на GitHub и выполнит bootstrap по `docs/AGENT-ONBOARDING.ru.md`.
Вам не нужно вручную настраивать MCP, пути и отдельный brain-репозиторий.

Переводы чеклиста для ИИ:

- `docs/AGENT-ONBOARDING.ru.md`
- `docs/AGENT-ONBOARDING.en.md`
- `docs/AGENT-ONBOARDING.es.md`
- `docs/AGENT-ONBOARDING.zh.md`

Переводы README:

- `README.en.md` — английская версия;
- `README.es.md` — испанская версия;
- `README.zh.md` — китайская версия.

## Правовой статус и SaaS

Проект `akasha-core` является проприетарным ядром AKASHA и распространяется **не** как open-source.
Все права принадлежат автору и владельцу репозитория `sikuykus-lab`.

Использование кода допускается только в рамках:

- интеграции с вашим приватным brain-репозиторием AKASHA (GitHub или сервер пользователя);
- AKASHA‑совместимых SaaS‑решений, явно одобренных владельцем.

Полный текст ограничений и разрешений:

- `LICENSE.md` — основная версия лицензии на русском;
- `LICENSE.en.md` — перевод на английский;
- `LICENSE.es.md` — перевод на испанский;
- `LICENSE.zh.md` — перевод на китайский.

## Установка (локально из исходников)

```bash
cd akasha-core
pip install -e .
```

## Быстрый старт

```bash
# bootstrap: SaaS → ваш private brain
python3 -m akash_core.cli onboard https://github.com/sikuykus-lab/akasha-core --agent cursor

# или если brain уже есть
akash adopt https://github.com/<your-user>/akash-brain --agent cursor

# проверить состояние
akash status

# старт сессии
akash pull

# sync в конце сессии
akash sync
```

Подробные команды и их назначение описаны в §11 `AKASHA-TZ v1.8`.

