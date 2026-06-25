from pathlib import Path


def test_pyproject_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "pyproject.toml").exists()


def test_package_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "akash_core").is_dir()

