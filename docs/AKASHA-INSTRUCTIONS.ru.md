AKASHA Core — инструкции (RU)
=============================

Этот документ описывает, как подключить и использовать AKASHA Core (`akasha-core`)
в соответствии с `AKASHA-TZ v1.8`.

1. Предусловия
--------------

- Установлен Python 3.11+.
- Установлен `git` и (для GitHub‑сценария) настроена аутентификация.
- Установлен пакет:

```bash
pip install git+https://github.com/sikuykus-lab/akasha-core.git
```

2. Вариант A — brain в private GitHub‑репозитории
-------------------------------------------------

1. Создайте или выберите private‑репозиторий с мозгом AKASHA, например:

   - `https://github.com/<user>/akash-brain`

2. На машине/в агрегаторе, где установлен `akasha-core`, выполните bootstrap:

   - В терминале:

     ```bash
     akash adopt https://github.com/<user>/akash-brain --agent cursor
     ```

   - Или фразой в чате агрегатору (Cursor, Claude Code и т.п.):

     > Настрой себя по данному проекту GitHub: `https://github.com/<user>/akash-brain`

3. После bootstrap:

   - `~/.akash/config.local` содержит `backend: github` и `brain_url`.
   - Локальный клон brain‑репозитория хранится в `~/.akash/github/<owner>/<repo>`.

3. Вариант B — brain на сервере пользователя
--------------------------------------------

1. На сервере создайте каталог под brain, например:

   - `~/.akash/brain`

2. Если агент уже работает на сервере (Hermes по SSH и т.п.):

   - Вызовите:

     ```bash
     akash adopt --server user@host:~/.akash/brain --agent hermes
     ```

   - Или фразой в чате агрегатору:

     > Используй мой сервер вместо GitHub для мозга AKASHA — `ssh user@host`, brain в `~/.akash/brain`

3. Для удалённого brain через SSH:

   - В конфиге `~/.akash/config.local` будет `backend: server`, `brain_host` и `brain_path`.

4. Основные команды CLI `akash`
-------------------------------

Все команды описаны в §11 `AKASHA-TZ v1.8`. Краткий список:

- `akash backend-detect` — проверка доступных backend'ов (`github` / `server`).
- `akash init` — инициализация структуры brain‑репозитория в текущем каталоге.
- `akash migrate` — миграция существующего brain до текущей схемы.
- `akash configure` — ручная правка `~/.akash/config.local` (backend, brain_url/brain_host, scope).
- `akash pull` — старт сессии: `pull` brain + чтение hot‑памяти (`persona`, `rapport`, `ACTIONS`).
- `akash prepare "…задача…"` — собрать pack skills для новой задачи.
- `akash read-skill <skill_id>` — прочитать `SKILL.md` из текущего pack.
- `akash remember "факт"` — записать факт в буфер сессии.
- `akash record-outcome <skill_id> <success|failure> [--help-score N]` — зафиксировать исход использования skill.
- `akash compact-check` — проверить, нужно ли сжатие hot‑памяти.
- `akash sync` — `pull → compact → NAV → push` brain.
- `akash harvest [--preview] [--merge]` — запуск урожая (harvest) по адаптерам.
- `akash import-legacy` — упрощённый режим harvest для SOUL/USER/MEMORY/AGENTS.
- `akash export-session` / `akash export-pack` / `akash ingest-session` — UPP‑транспорт для агрегаторов без tools.
- `akash status` — показать текущий `brain_version`, backend и базовую информацию.

5. Типичный жизненный цикл сессии
---------------------------------

1. Агрегатор создаёт новый чат → lifecycle‑hook вызывает:

   ```bash
   akash pull
   ```

2. При новой задаче агрегатор вызывает:

   ```bash
   akash prepare "описание задачи"
   akash read-skill <skill_id>   # по мере необходимости
   ```

3. В процессе работы:

   ```bash
   akash remember "факт о пользователе/задаче"
   akash record-outcome <skill_id> success --help-score 1
   ```

4. Периодически и в конце сессии:

   ```bash
   akash sync
   ```

