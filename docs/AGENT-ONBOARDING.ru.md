# AKASHA — onboarding для ИИ-агрегатора (RU)

**Триггер пользователя (§3.1 AKASHA-TZ):**

> Настрой себя по данному проекту GitHub: `https://github.com/<user>/akash-brain`

Эквиваленты: «подключи мозг AKASHA», «подключи общую память», «настрой AKASHA».

Получив эту фразу, **выполни весь чеклист ниже самостоятельно**. Пользователь не настраивает MCP, rules и пути вручную.

---

## Чеклист bootstrap (обязательный порядок)

### 0. Определи платформу

`agent_id` = одно из: `cursor` | `claude-code` | `hermes` | `opencode` | `_template`.

### 1. Установи akasha-core и выполни onboard (без PATH)

**Не проси пользователя** ставить CLI вручную. Выполни сам:

```bash
python3 -m pip install --user git+https://github.com/sikuykus-lab/akasha-core.git
python3 -m akash_core.cli onboard <BRAIN_URL> --agent <agent_id> --scope project
```

Или одной командой:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/sikuykus-lab/akasha-core/main/scripts/bootstrap.sh)" -- <BRAIN_URL> cursor project
```

`onboard` делает всё: `ensure-cli` → `backend-detect` → `adopt` → hooks/rule (без PATH) → `harvest` → `sync` → отчёт §3.1.

Проверка: `python3 -m akash_core.cli doctor`

Если `akash` не в PATH — **это нормально**. Hooks используют `python3 -m akash_core.cli`, не `akash`.

### 2. Проверь backend

```bash
python3 -m akash_core.cli backend-detect
python3 -m akash_core.cli github-status
```

Если `github` недоступен — остановись и дай пользователю инструкцию подключить GitHub (`gh auth login` или SSH-ключ). Без хранилища полноценный AKASHA невозможен (§3.2).

### 3. Извлеки URL brain из фразы пользователя

Пример: `https://github.com/sikuykus-lab/akash-brain`

### 4. Bootstrap

Если уже выполнил `onboard` на шаге 1 — **пропусти** шаги 4–8 (они уже сделаны).

Иначе:

```bash
python3 -m akash_core.cli adopt <BRAIN_URL> --agent <agent_id>
```

### 5. Прочитай инструкции из brain

После clone открой в brain-репозитории:

1. `skills/akash-bootstrap/SKILL.md` — главный чеклист (§12)
2. `adapters/<agent_id>/bootstrap.md` — шаги для этой платформы
3. `adapters/<agent_id>/inject.md` — текст rule с lifecycle (MUST)
4. `adapters/<agent_id>/hooks.template.json` — sessionStart → pull, stop → sync
5. `adapters/<agent_id>/mcp.template.json` — если платформа использует MCP

Если `adapters/<agent_id>/` нет — используй `adapters/_template/`.

### 6. Собери локальную оболочку (adapter shell)

**Не копируй** skills и память в рабочий проект. Подключи brain как единственный источник.

| Механизм | Cursor (пример) |
|----------|-----------------|
| Lifecycle rule | `.cursor/rules/akasha-lifecycle.mdc` с `alwaysApply: true` — текст из `inject.md` |
| Hooks | `.cursor/hooks.json` из `hooks.template.json` |
| MCP | `.cursor/mcp.json` — запись из `mcp.template.json` |
| Config | `~/.akash/config.local` уже записан при `adopt` |

Спроси пользователя **scope**: `project` (только этот проект) или `user` (все проекты на машине). Запиши:

```bash
akash configure --backend github --brain-url <BRAIN_URL> --agent-id <agent_id> --scope project
# или --scope user
```

### 7. Harvest (урожай)

```bash
akash harvest --preview
```

Покажи отчёт пользователю. После подтверждения:

```bash
akash harvest
akash sync
```

При повторном агрегаторе на тот же brain: `akash harvest --merge`.

### 8. Проверка

```bash
akash pull
akash status
```

Убедись: `brain_version`, hot-память (`persona`, `rapport`, `ACTIONS`), backend `github`.

### 9. Финальное сообщение пользователю (§3.1)

> **Готов к работе. Мы — есть AKASHA.**  
> Brain vN · `<agent_id>` · `<транспорт>` · `github` · N skills (M импортировано при установке)  
> Профиль и память собраны из ваших проектов. Следующий агрегатор: **та же ссылка** на brain.

---

## Контракт после bootstrap (все новые чаты)

```
sessionStart  → akash pull
новая задача  → akash prepare → read-skill (только из pack)
работа          → remember, record-outcome
конец           → akash sync
```

**Запрещено:** читать каталог `skills/` целиком, `@`-ить все skills — только через `prepare` / `read-skill`.

---

## Ссылки

- Ядро: https://github.com/sikuykus-lab/akasha-core
- Инструкции: `docs/AKASHA-INSTRUCTIONS.ru.md`
- ТЗ: AKASHA-TZ v1.8
