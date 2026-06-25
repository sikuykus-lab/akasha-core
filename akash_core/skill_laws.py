from __future__ import annotations

import re
from dataclasses import dataclass

# Закон I — экономия токенов (§1)
MAX_SKILL_BYTES = 4_096

TRIGGER_HEADERS = ("## triggers", "## триггеры", "## when", "## когда")
STEP_HEADERS = ("## steps", "## шаги", "## workflow", "## как")
PURPOSE_HEADERS = ("## назначение", "## purpose", "## capability", "## возможность")


@dataclass
class LawResult:
    ok: bool
    violations: list[str]


def validate_skill_md(content: str) -> LawResult:
    """Проверка skill на три закона AKASHA (§1, §14.4)."""
    violations: list[str] = []
    raw = content.encode("utf-8")
    if len(raw) > MAX_SKILL_BYTES:
        violations.append(f"Law I: skill {len(raw)} B > {MAX_SKILL_BYTES} B")

    lower = content.lower()
    if not any(h in lower for h in TRIGGER_HEADERS):
        violations.append("Law II: нет секции Triggers / Триггеры")

    if not any(h in lower for h in STEP_HEADERS):
        violations.append("Law III: нет секции Steps / Шаги")

    if not extract_purpose(content):
        violations.append("Law IV: нет секции Назначение / Purpose (журнал возможности)")

    code_blocks = re.findall(r"```[\s\S]*?```", content)
    code_bytes = sum(len(b.encode()) for b in code_blocks)
    if code_bytes > MAX_SKILL_BYTES // 2:
        violations.append("Law I: слишком много кода в skill")

    steps_text = _extract_after_header(content, STEP_HEADERS)
    bullet_lines = [ln for ln in steps_text.splitlines() if re.match(r"^\s*[-*\d.]", ln.strip())]
    if len(bullet_lines) < 2:
        violations.append("Law III: нужно ≥2 actionable шагов")

    return LawResult(ok=not violations, violations=violations)


def _extract_after_header(content: str, headers: tuple[str, ...]) -> str:
    lower = content.lower()
    for h in headers:
        idx = lower.find(h)
        if idx >= 0:
            return content[idx + len(h) :]
    return ""


def extract_purpose(content: str) -> str:
    """Одна строка журнала: зачем эта возможность."""
    section = _extract_after_header(content, PURPOSE_HEADERS)
    for line in section.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^[-*]\s*", "", line)
        if line:
            return line[:240]
    return ""
