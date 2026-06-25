from __future__ import annotations

import re

# RU ↔ EN и смежные токены для матча задачи с тегами skills
TOKEN_ALIASES: dict[str, set[str]] = {
    "игра": {"game", "games"},
    "игру": {"game", "games"},
    "игры": {"game", "games"},
    "игр": {"game", "games"},
    "спрайт": {"sprite", "sprites"},
    "спрайты": {"sprite", "sprites"},
    "спрайтами": {"sprite", "sprites"},
    "уровень": {"level", "levels"},
    "уровни": {"level", "levels"},
    "уровнями": {"level", "levels"},
    "браузер": {"browser", "web", "html"},
    "браузерную": {"browser", "web", "html"},
    "браузерная": {"browser", "web", "html"},
    "страница": {"page", "html", "web", "site"},
    "страницу": {"page", "html", "web", "site", "streamlit", "dataroom"},
    "страницы": {"page", "html", "web", "site", "streamlit", "dataroom"},
    "localhost": {"localhost", "local", "streamlit", "http"},
    "локальный": {"localhost", "local"},
    "локальную": {"localhost", "local"},
    "локальном": {"localhost", "local"},
    "хост": {"host", "localhost", "server"},
    "сайт": {"site", "web", "html"},
    "веб": {"web", "html", "browser"},
    "проверк": {"check", "verify", "rm"},
    "сотрудник": {"employee", "staff", "rm"},
    "рассылк": {"mail", "digest", "send", "rassylka"},
    "дат": {"date", "trigger"},
    "дашборд": {"dashboard", "streamlit", "bi"},
    "график": {"chart", "plot", "streamlit"},
    "таблиц": {"sheet", "sheets", "google"},
    "скрипт": {"script", "apps", "gas"},
    "игр": {"game", "preview"},
    "простую": {"simple", "minimal"},
}


def base_tokenize(text: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9]+", text) if len(w) > 2}


def expand_task_tokens(task: str) -> set[str]:
    """Токены задачи + синонимы RU↔EN."""
    base = base_tokenize(task)
    expanded = set(base)
    for tok in base:
        if tok in TOKEN_ALIASES:
            expanded |= TOKEN_ALIASES[tok]
        for key, aliases in TOKEN_ALIASES.items():
            if len(key) >= 4 and (key in tok or tok in key):
                expanded |= aliases
    return expanded
