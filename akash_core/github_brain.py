from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.parse import urlparse

AKASHA_CORE_REPO = "https://github.com/sikuykus-lab/akasha-core"
DEFAULT_BRAIN_NAME = "akash-brain"


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def gh_available() -> bool:
    return _run(["gh", "--version"]).returncode == 0


def get_gh_user() -> str:
    if not gh_available():
        raise SystemExit(
            "GitHub CLI (gh) не найден. Выполните `gh auth login` — без этого private brain на вашем аккаунте не создать."
        )
    r = _run(["gh", "api", "user", "-q", ".login"])
    if r.returncode != 0:
        raise SystemExit(f"gh auth failed: {r.stderr.strip() or r.stdout}")
    user = r.stdout.strip()
    if not user:
        raise SystemExit("Не удалось определить GitHub user. Выполните `gh auth login`.")
    return user


def parse_github_owner(url: str) -> str | None:
    url = url.rstrip("/").removesuffix(".git")
    if "github.com" not in url:
        return None
    parts = urlparse(url).path.strip("/").split("/")
    return parts[0] if parts else None


def is_akasha_core_url(url: str) -> bool:
    u = url.lower()
    return "akasha-core" in u or u.endswith("sikuykus-lab/akasha-core")


def brain_repo_url(owner: str, name: str = DEFAULT_BRAIN_NAME) -> str:
    return f"https://github.com/{owner}/{name}"


def repo_exists(owner: str, name: str) -> bool:
    return _run(["gh", "repo", "view", f"{owner}/{name}"]).returncode == 0


def create_private_brain_repo(owner: str, name: str = DEFAULT_BRAIN_NAME) -> str:
    if repo_exists(owner, name):
        return brain_repo_url(owner, name)
    r = _run(
        [
            "gh",
            "repo",
            "create",
            name,
            "--private",
            "--description",
            "AKASHA private brain — personal memory and skills",
        ]
    )
    if r.returncode != 0:
        raise SystemExit(f"Не удалось создать private brain: {r.stderr or r.stdout}")
    return brain_repo_url(owner, name)


def ensure_user_brain_repo(name: str = DEFAULT_BRAIN_NAME) -> str:
    """
    Создать private akash-brain на GitHub **текущего** пользователя (gh auth).
    """
    user = get_gh_user()
    url = create_private_brain_repo(user, name)
    print(f"Brain repository: {url} (private, owner={user})")
    return url


def resolve_brain_url(user_input: str | None) -> str:
    """
    Разрешить URL brain для onboard.

    - Ссылка на akasha-core (публичный SaaS) → создать brain у пользователя.
    - Ссылка на чужой akash-brain → предупреждение + brain у пользователя.
    - Ссылка на свой akash-brain → использовать.
    - Пусто / «настрой AKASHA» → brain у пользователя.
    """
    if not user_input or not user_input.strip():
        return ensure_user_brain_repo()

    url = user_input.strip().rstrip("/")

    if is_akasha_core_url(url):
        print("SaaS akasha-core detected — создаём private brain на вашем GitHub.")
        return ensure_user_brain_repo()

    owner = parse_github_owner(url)
    if not owner:
        raise SystemExit(f"Не GitHub URL: {url}")

    try:
        gh_user = get_gh_user()
    except SystemExit:
        raise

    if owner.lower() != gh_user.lower():
        print(
            f"Репозиторий {url} принадлежит не вам ({owner} ≠ {gh_user}).\n"
            f"Создаём ваш private brain: {brain_repo_url(gh_user)}"
        )
        return ensure_user_brain_repo()

    if not repo_exists(owner, DEFAULT_BRAIN_NAME) and DEFAULT_BRAIN_NAME in url:
        return create_private_brain_repo(owner, DEFAULT_BRAIN_NAME)

    # Проверка доступа
    repo_slug = "/".join(urlparse(url).path.strip("/").split("/")[:2])
    if _run(["gh", "repo", "view", repo_slug]).returncode != 0:
        raise SystemExit(
            f"Нет доступа к {url}. Это private-репозиторий другого аккаунта.\n"
            f"Используйте SaaS: {AKASHA_CORE_REPO} — AKASHA создаст brain на вашем профиле."
        )
    return url


def initial_push_if_needed(brain_path: Path, message: str = "AKASHA brain scaffold") -> None:
    """Первый commit+push после scaffold в пустом brain."""
    if not (brain_path / ".git").exists():
        return
    status = _run(["git", "status", "--porcelain"], cwd=brain_path)
    if not status.stdout.strip():
        # maybe empty repo with no commits
        heads = _run(["git", "rev-parse", "HEAD"], cwd=brain_path)
        if heads.returncode == 0:
            return
    _run(["git", "add", "-A"], cwd=brain_path)
    _run(["git", "commit", "-m", message], cwd=brain_path)
    branch = _run(["git", "branch", "--show-current"], cwd=brain_path).stdout.strip() or "main"
    _run(["git", "push", "-u", "origin", branch], cwd=brain_path)
