AKASHA Core (`akasha-core`)
===========================

Python-ядро **AKASHA** — общая память и skills для AI-агентов (Cursor, Claude Code, Hermes и др.).

- Один **brain** (private GitHub или каталог на сервере) — persona, rapport, skills, NAV.
- CLI `akash` и библиотека `akash_core`.
- Backend: `github` или `server`.
- Onboard **одной фразой** в чат — агент сам ставит ядро и создаёт ваш private `akash-brain`.

**Переводы:** [English](README.en.md) · [中文](README.zh.md)

## Одна фраза в чат

При настроенном GitHub (`gh auth login` или SSH):

> **Настрой себя по данному проекту GitHub:** `https://github.com/sikuykus-lab/akasha-core`

Агент выполняет bootstrap по `docs/AGENT-ONBOARDING.ru.md`. Чеклисты: `docs/AGENT-ONBOARDING.en.md`, `docs/AGENT-ONBOARDING.zh.md`.

## Установка

```bash
python3 -m pip install --user git+https://github.com/sikuykus-lab/akasha-core.git
```

Из исходников (разработка):

```bash
cd akasha-core && pip install -e .
```

## Быстрый старт

```bash
# полный bootstrap: SaaS → ваш private brain → hooks → harvest
python3 -m akash_core.cli onboard https://github.com/sikuykus-lab/akasha-core --agent cursor

# brain уже есть
akash adopt https://github.com/<your-user>/akash-brain --agent cursor

# brain на сервере
akash adopt --server user@host:~/.akash/brain --agent hermes

akash status
akash pull
akash sync
```

## Команды CLI

| Команда | Назначение |
|---------|------------|
| `akash onboard [url]` | Полный bootstrap: install → brain → shell → harvest → sync |
| `akash adopt <url>` | Подключить существующий brain (GitHub URL) |
| `akash adopt --server <user@host:path>` | Brain на сервере пользователя |
| `akash create-brain` | Создать private `akash-brain` на GitHub |
| `akash install-shell` | Переустановить hooks и rule Cursor после обновления |
| `akash doctor` | Диагностика CLI, config, brain, GitHub |
| `akash ensure-cli` | Установить `akasha-core`, если отсутствует |
| `akash backend-detect` | Доступные backend: `github` / `server` |
| `akash github-status` | Статус аутентификации GitHub |
| `akash init` | Scaffold brain в текущем каталоге |
| `akash migrate` | Миграция brain к актуальной схеме |
| `akash configure` | Ручная правка `~/.akash/config.local` |
| `akash pull` | Старт сессии: pull + hot-память (persona, rapport, ACTIONS) |
| `akash prepare "задача"` | Собрать pack skills под задачу |
| `akash read-skill <id>` | Прочитать SKILL.md из текущего pack |
| `akash remember "факт"` | Записать факт в буфер сессии |
| `akash record-outcome <id> success\|failure` | Исход использования skill → usage.jsonl |
| `akash compact-check` | Нужно ли сжатие hot-памяти |
| `akash sync` | pull → compact → NAV → push в brain |
| `akash harvest [--preview] [--merge]` | Урожай из агрегатора в brain |
| `akash import-legacy` | Узкий harvest: SOUL/USER/MEMORY/AGENTS |
| `akash export-session --agent <id>` | UPP: память для вставки в чат |
| `akash export-pack "задача" --agent <id>` | UPP: pack по задаче |
| `akash ingest-session --agent <id>` | UPP: разбор блока AKASHA-INGEST |
| `akash status` | brain_version, backend, scope |

MCP-tools (если подключены) — зеркало тех же операций.

## Жизненный цикл сессии

```
sessionStart  →  akash pull
новая задача  →  akash prepare "…"  →  akash read-skill <id>
работа          →  akash remember  ·  akash record-outcome
конец           →  akash sync
```

Skills читать **только** через `prepare` / `read-skill`, не каталог `skills/` целиком.

## Правовой статус

`akasha-core` — **проприетарное** ядро AKASHA, не open source. Права: `sikuykus-lab`.

Разрешено: интеграция с **вашим** private brain; AKASHA‑совместимые SaaS по согласованию с правообладателем.

- [LICENSE.md](LICENSE.md) — русский (юридический текст)
- [LICENSE.en.md](LICENSE.en.md) · [LICENSE.zh.md](LICENSE.zh.md) — переводы

Подробнее для пользователя: `docs/AKASHA-INSTRUCTIONS.ru.md` (en/zh в той же папке).
