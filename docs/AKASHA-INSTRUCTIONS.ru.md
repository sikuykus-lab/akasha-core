AKASHA Core — инструкции (RU)
=============================

Краткое руководство по `akasha-core`. **Полный список команд** — в [README.md](../README.md).

## 1. Предусловия

- Python 3.11+
- `git`; для GitHub — `gh auth login` или SSH
- Установка:

```bash
python3 -m pip install --user git+https://github.com/sikuykus-lab/akasha-core.git
```

## 2. Bootstrap (рекомендуется)

Фраза агенту:

> **Настрой себя по данному проекту GitHub:** `https://github.com/sikuykus-lab/akasha-core`

Терминал:

```bash
python3 -m akash_core.cli onboard https://github.com/sikuykus-lab/akasha-core --agent cursor
```

После onboard: `~/.akash/config.local`, клон brain в `~/.akash/github/<user>/akash-brain`.

Чеклист для ИИ: `docs/AGENT-ONBOARDING.ru.md`.

## 3. Brain уже есть

```bash
akash adopt https://github.com/<user>/akash-brain --agent cursor
```

## 4. Brain на сервере

```bash
akash adopt --server user@host:~/.akash/brain --agent hermes
```

## 5. Жизненный цикл

**Сначала паутина** — `prepare` смотрит, есть ли готовые lego-кубики; не блокирует работу.

```bash
akash pull
akash prepare "описание задачи"
akash read-skill <skill_id>
akash remember "факт"
akash record-outcome <skill_id> success
akash sync
```

## 6. Диагностика

```bash
akash doctor
akash status
akash install-shell   # после обновления ядра
```
