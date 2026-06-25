AKASHA Core (`akasha-core`)
===========================

Это Python-реализация ядра AKASHA (`akash-core v1`) строго по документу `AKASHA-TZ v1.8`.

- Один brain-репозиторий (GitHub private или каталог на сервере) с фиксированной структурой.
- CLI `akash` и библиотека `akash_core` для операций `adopt`, `pull`, `prepare`, `remember`, `sync` и др.
- Поддержка backend'ов `github` и `server` как в разделе §2.5 ТЗ.

Единственный источник правды по поведению — файл ТЗ:

- `AKASHA-TZ v1.8` (копия в рабочем репозитории пользователя, например `Google Sheets/akash/AKASHA-TZ.md`).

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
# bootstrap по GitHub brain-репо
akash adopt https://github.com/user/akash-brain --agent cursor

# проверить состояние
akash status

# старт сессии
akash pull

# sync в конце сессии
akash sync
```

Подробные команды и их назначение описаны в §11 `AKASHA-TZ v1.8`.

