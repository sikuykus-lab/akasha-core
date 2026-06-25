from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from .skill_laws import validate_skill_md

MAX_STEP_LINES = 8

# Каталоги без сканирования (§14.2)
SKIP_DIR_NAMES = {
    ".git",
    ".cursor",
    ".akash",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".venv",
    "venv",
    "akasha-core",
    "akash-brain",
    "дубли",
    "личная-информация",
    "документация",
}

# Расширения → теги стека
STACK_BY_EXT = {
    ".gs": ["apps-script", "gas", "google-sheets"],
    ".py": ["python"],
    ".ts": ["typescript"],
    ".tsx": ["typescript", "react"],
    ".js": ["javascript"],
    ".sh": ["shell", "ops"],
    ".md": ["docs"],
}

# Маркеры проекта в корне
PROJECT_MARKERS = (
    "README.md",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "apps-script",
)


@dataclass
class ProjectInfo:
    name: str
    root: Path
    tags: list[str] = field(default_factory=list)
    readme_excerpt: str = ""


@dataclass
class SynthesisReport:
    projects: int = 0
    chunks_found: int = 0
    imported: int = 0
    merged: int = 0
    drafts: int = 0
    skipped: int = 0
    skill_ids: list[str] = field(default_factory=list)


def _slug(text: str, max_len: int = 40) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    if not text:
        text = "chunk"
    return text[:max_len].strip("-")


def discover_projects(workspace: Path, max_depth: int = 2) -> list[ProjectInfo]:
    """Найти рабочие каталоги с признаками агентной работы (§14.2)."""
    workspace = workspace.resolve()
    found: list[ProjectInfo] = []

    def _scan_dir(base: Path, depth: int) -> None:
        if depth > max_depth:
            return
        if not base.is_dir():
            return
        if base.name in SKIP_DIR_NAMES or base.name.startswith("."):
            return

        if depth == 0:
            try:
                children = [c for c in base.iterdir() if c.is_dir()]
            except OSError:
                return
            for child in children:
                _scan_dir(child, depth + 1)
            return

        has_marker = any((base / m).exists() for m in PROJECT_MARKERS)
        has_code = any(
            p.suffix in STACK_BY_EXT and p.is_file()
            for p in base.iterdir()
            if p.is_file()
        ) or (base / "apps-script").is_dir()

        if has_marker or has_code:
            info = _build_project_info(base)
            if info:
                found.append(info)

    _scan_dir(workspace, 0)
    # дедуп по пути
    seen: set[Path] = set()
    unique: list[ProjectInfo] = []
    for p in found:
        if p.root not in seen:
            seen.add(p.root)
            unique.append(p)
    return unique


def _build_project_info(root: Path) -> ProjectInfo | None:
    tags: set[str] = set()
    readme = root / "README.md"
    excerpt = ""
    if readme.is_file():
        text = readme.read_text(encoding="utf-8", errors="replace")[:800]
        excerpt = text.strip()
        tags.add("documented")

    if (root / "apps-script").is_dir() or list(root.glob("*.gs")):
        tags.update(["apps-script", "gas", "google-sheets"])
    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        tags.add("python")
    if (root / "package.json").exists():
        tags.add("nodejs")
    if "streamlit" in root.name.lower() or (root / "streamlit_dashboard_mcp.py").exists():
        tags.add("streamlit")
    if "powerbi" in root.name.lower():
        tags.add("powerbi")
    if root.name.lower() in ("akashi", "akash"):
        tags.update(["vpn", "android", "kotlin"])

    py_files = list(root.rglob("*.py"))[:50]
    if any("streamlit" in f.read_text(encoding="utf-8", errors="ignore")[:2000].lower() for f in py_files if f.is_file()):
        tags.add("streamlit")

    if not tags and not excerpt:
        return None

    return ProjectInfo(name=root.name, root=root, tags=sorted(tags), readme_excerpt=excerpt)


def _key_files(project: ProjectInfo) -> list[Path]:
    """Атомарные «кубики» — ключевые файлы проекта (§14.4)."""
    root = project.root
    files: list[Path] = []

    gas_dir = root / "apps-script"
    if gas_dir.is_dir():
        files.extend(sorted(gas_dir.glob("*.gs"))[:20])

    for pattern in ("main.py", "server.py", "app.py", "cli.py"):
        p = root / pattern
        if p.is_file():
            files.append(p)

    if not files:
        for p in sorted(root.rglob("*")):
            if p.is_file() and p.suffix in STACK_BY_EXT and p.name not in ("__init__.py",):
                if any(part in SKIP_DIR_NAMES for part in p.parts):
                    continue
                files.append(p)
                if len(files) >= 15:
                    break

    return files


def _extract_functions(text: str) -> list[str]:
    names: list[str] = []
    for m in re.finditer(r"function\s+(\w+)", text):
        names.append(m.group(1))
    for m in re.finditer(r"^def\s+(\w+)\s*\(", text, re.MULTILINE):
        names.append(m.group(1))
    return names[:8]


def synthesize_skill_md(project: ProjectInfo, file_path: Path) -> tuple[str, str, list[str]]:
    """Сгенерировать lego-skill из одного файла проекта."""
    rel = file_path.relative_to(project.root)
    skill_id = _slug(f"{project.name}-{rel.stem}")[:48]
    text = file_path.read_text(encoding="utf-8", errors="replace")
    funcs = _extract_functions(text)
    tags = sorted(set(project.tags + STACK_BY_EXT.get(file_path.suffix, [])))

    triggers = [project.name, file_path.stem, file_path.suffix.lstrip(".")]
    triggers.extend(funcs[:5])
    if "gas" in tags:
        triggers.extend(["google sheets", "apps script", "рассылка"])

    steps = [
        f"Открой `{rel}` в проекте `{project.name}`.",
        "Сверься с существующими функциями: " + (", ".join(funcs[:6]) if funcs else "см. файл."),
        "Правь точечно; не дублируй логику из других skills в brain (Law II).",
        "После изменений — `remember` + `sync` в AKASHA.",
    ]
    purpose_line = f"Работа с `{rel}` в `{project.name}`"
    if funcs:
        purpose_line += f" — функции: {', '.join(funcs[:4])}"
    if project.readme_excerpt:
        first_line = project.readme_excerpt.splitlines()[0][:120]
        steps.insert(1, f"Контекст проекта: {first_line}")

    anti = [
        "Не копировать весь файл в контекст чата (Law I).",
        "Не создавать второй skill на тот же файл — merge (§14.5).",
    ]

    lines = [
        f"# {skill_id}",
        "",
        f"tags: {', '.join(tags)}",
        f"project: {project.name}",
        f"source: {rel}",
        "",
        "## Назначение",
        purpose_line,
        "",
        "## Триггеры",
        *[f"- {t}" for t in dict.fromkeys(triggers) if t],
        "",
        "## Шаги",
        *[f"{i}. {s}" for i, s in enumerate(steps[:MAX_STEP_LINES], 1)],
        "",
        "## Paths",
        f"- `{rel}`",
        "",
        "## Антипаттерны",
        *[f"- {a}" for a in anti],
    ]
    if funcs:
        lines.extend(["", "## Entrypoints", *[f"- `{fn}()`" for fn in funcs]])

    content = "\n".join(lines) + "\n"
    return skill_id, content, tags


def run_project_synthesis(
    brain_path: Path,
    workspace: Path,
    *,
    preview: bool,
    merge: bool,
) -> SynthesisReport:
    """§14.4 — синтез lego-skills из рабочих проектов."""
    from .nav_map import register_chunks

    report = SynthesisReport()
    projects = discover_projects(workspace)
    report.projects = len(projects)

    chunks_for_nav: list[dict] = []

    for project in projects:
        for file_path in _key_files(project):
            report.chunks_found += 1
            skill_id, content, tags = synthesize_skill_md(project, file_path)
            law = validate_skill_md(content)

            dest_dir = brain_path / "skills" / skill_id
            draft_dir = brain_path / "skills" / "_drafts" / skill_id
            dest = dest_dir / "SKILL.md"
            draft = draft_dir / "SKILL.md"

            if preview:
                if law.ok:
                    report.imported += 1
                else:
                    report.drafts += 1
                report.skill_ids.append(skill_id)
                continue

            if dest.exists() and not merge and law.ok:
                report.skipped += 1
                continue

            if law.ok:
                dest_dir.mkdir(parents=True, exist_ok=True)
                if dest.exists() and merge:
                    existing = dest.read_text(encoding="utf-8", errors="replace")
                    if content.strip() in existing:
                        report.skipped += 1
                        continue
                    dest.write_text(existing + f"\n\n[harvest-synth:{file_path}]\n\n{content}", encoding="utf-8")
                    report.merged += 1
                else:
                    dest.write_text(content, encoding="utf-8")
                    report.imported += 1
                chunks_for_nav.append(
                    {
                        "id": skill_id,
                        "tags": tags,
                        "project": project.name,
                        "paths": [str(file_path.relative_to(project.root))],
                    }
                )
            else:
                draft_dir.mkdir(parents=True, exist_ok=True)
                draft_content = content + "\n## Law violations\n" + "\n".join(f"- {v}" for v in law.violations) + "\n"
                draft.write_text(draft_content, encoding="utf-8")
                report.drafts += 1

            report.skill_ids.append(skill_id)

    if not preview and chunks_for_nav:
        register_chunks(brain_path, chunks_for_nav)
        from .capabilities import rebuild_from_skills

        rebuild_from_skills(brain_path)

    return report
