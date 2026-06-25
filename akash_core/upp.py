from __future__ import annotations

from pathlib import Path

from .session import load_hot_memory


def cli_export_session(agent: str) -> None:
    """
    export-session → UPP-блок с hot-памятью (§2.3).
    """
    # Без brain_path здесь мы пока используем фиктивное значение; в реальной интеграции
    # агрегатор должен передавать путь к brain.
    brain_path = Path(".")  # placeholder
    hot = load_hot_memory(brain_path)
    print("<!-- AKASHA-SESSION v1 agent={} -->".format(agent))
    print("## Memory (read-only)")
    for chunk in (hot.persona, hot.rapport, hot.actions):
        if chunk:
            print(chunk)
    print("## Pack")
    print("## End contract")
    print("В конце ответь блоком <!-- AKASHA-INGEST --> с фактами для remember.")


def cli_export_pack(agent: str, task: str) -> None:
    """
    export-pack → UPP-pack блок (§2.3).
    """
    print("<!-- AKASHA-SESSION v1 agent={} -->".format(agent))
    print("## Pack")
    print(task)
    print("## End contract")


def cli_ingest_session(agent: str, stdin: str) -> None:
    """
    Разбор AKASHA-INGEST из stdin (§2.3, §4).
    Здесь пока просто печатаем вход для отладки.
    """
    print(f"AKASHA-INGEST for agent={agent}:")
    print(stdin)

