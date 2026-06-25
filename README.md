AKASHA Core (`akasha-core`)
===========================

Это Python-реализация ядра AKASHA (`akash-core v1`) строго по документу `AKASHA-TZ v1.8`.

- Один brain-репозиторий (GitHub private или каталог на сервере) с фиксированной структурой.
- CLI `akash` и библиотека `akash_core` для операций `adopt`, `pull`, `prepare`, `remember`, `sync` и др.
- Поддержка backend'ов `github` и `server` как в разделе §2.5 ТЗ.

Единственный источник правды по поведению — файл ТЗ:

- `AKASHA-TZ v1.8` (копия в рабочем репозитории пользователя, например `Google Sheets/akash/AKASHA-TZ.md`).

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

