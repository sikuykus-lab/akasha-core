# AKASHA — onboarding для ИИ-агрегатора (RU)

## Два репозитория

| Репозиторий | Кто владеет | Доступ | Назначение |
|-------------|-------------|--------|------------|
| **akasha-core** (SaaS) | `sikuykus-lab` | публичный | CLI, документация, шаблоны, установка |
| **akash-brain** | **пользователь** | private | persona, память, skills — «общее сознание» |

**Не указывайте** чужой private brain (`sikuykus-lab/akash-brain` и т.п.) — агент не получит доступ.
Указывайте **публичный SaaS** — AKASHA сам создаст `https://github.com/<ваш-user>/akash-brain`.

**Триггер пользователя (§3.1 AKASHA-TZ):**

> Настрой себя по данному проекту GitHub: `https://github.com/sikuykus-lab/akasha-core`

Эквиваленты: «подключи мозг AKASHA», «подключи общую память», «настрой AKASHA».

Получив эту фразу, **выполни весь чеклист ниже самостоятельно**. Пользователь не настраивает MCP, rules и пути вручную.

**Перед onboard:** `gh auth login` (или SSH-ключ с доступом к GitHub). Без этого private brain на профиле пользователя не создать.

---

## Чеклист bootstrap (обязательный порядок)

### 0. Определи платформу

`agent_id` = одно из: `cursor` | `claude-code` | `hermes` | `opencode` | `_template`.

### 1. Установи akasha-core и выполни onboard (без PATH)

**Не проси пользователя** ставить CLI вручную. Выполни сам:

```bash
python3 -m pip install --user git+https://github.com/sikuykus-lab/akasha-core.git
python3 -m akash_core.cli onboard https://github.com/sikuykus-lab/akasha-core --agent <agent_id> --scope project
```

Или без URL (то же самое — brain создастся автоматически):

```bash
python3 -m akash_core.cli onboard --agent <agent_id> --scope project
```

Или одной командой:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/sikuykus-lab/akasha-core/main/scripts/bootstrap.sh)" -- cursor project
```

`onboard` делает всё: install → `gh` → **создание private brain на GitHub пользователя** → adopt → hooks/rule → harvest → sync → отчёт §3.1.

Проверка: `python3 -m akash_core.cli doctor`

Если `akash` не в PATH — **это нормально**. Hooks используют `python3 -m akash_core.cli`, не `akash`.

### 2. Проверь backend

```bash
python3 -m akash_core.cli backend-detect
python3 -m akash_core.cli github-status
```

Если `github` недоступен — остановись и дай пользователю инструкцию: `gh auth login`. Без хранилища полноценный AKASHA невозможен (§3.2).

### 3. URL из фразы пользователя

- `https://github.com/sikuykus-lab/akasha-core` → SaaS, brain создаётся у пользователя.
- `https://github.com/<user>/akash-brain` (свой) → использовать существующий.
- Чужой private brain → onboard создаст brain на профиле пользователя и предупредит.

### 4–8. Если уже выполнил `onboard` на шаге 1 — пропусти

Иначе вручную: `adopt`, harvest, sync — см. `docs/AKASHA-INSTRUCTIONS.ru.md`.

### 9. Финальное сообщение пользователю (§3.1)

> **Готов к работе. Мы — есть AKASHA.**  
> Brain vN · `<agent_id>` · `github` · `https://github.com/<user>/akash-brain`  
> SaaS: `https://github.com/sikuykus-lab/akasha-core`  
> Профиль и память собраны из ваших проектов. Следующий агрегатор: **та же ссылка на akasha-core** или «настрой AKASHA».

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

- SaaS (публичный): https://github.com/sikuykus-lab/akasha-core
- Инструкции: `docs/AKASHA-INSTRUCTIONS.ru.md`
- ТЗ: AKASHA-TZ v1.8
