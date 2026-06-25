from unittest.mock import patch

from akash_core import github_brain as gb


def test_is_akasha_core_url():
    assert gb.is_akasha_core_url("https://github.com/sikuykus-lab/akasha-core")
    assert gb.is_akasha_core_url("https://github.com/sikuykus-lab/akasha-core/")
    assert not gb.is_akasha_core_url("https://github.com/alice/akash-brain")


def test_parse_github_owner():
    assert gb.parse_github_owner("https://github.com/foo/bar") == "foo"
    assert gb.parse_github_owner("https://github.com/foo/bar.git") == "foo"
    assert gb.parse_github_owner("not-a-url") is None


@patch("akash_core.github_brain.ensure_user_brain_repo", return_value="https://github.com/me/akash-brain")
def test_resolve_saas_creates_user_brain(mock_ensure):
    url = gb.resolve_brain_url("https://github.com/sikuykus-lab/akasha-core")
    assert url == "https://github.com/me/akash-brain"
    mock_ensure.assert_called_once()


@patch("akash_core.github_brain.ensure_user_brain_repo", return_value="https://github.com/me/akash-brain")
def test_resolve_empty_creates_user_brain(mock_ensure):
    url = gb.resolve_brain_url(None)
    assert url == "https://github.com/me/akash-brain"
    mock_ensure.assert_called_once()


@patch("akash_core.github_brain._run")
@patch("akash_core.github_brain.get_gh_user", return_value="me")
def test_resolve_own_brain_url(mock_user, mock_run):
    mock_run.return_value.returncode = 0
    url = gb.resolve_brain_url("https://github.com/me/akash-brain")
    assert url == "https://github.com/me/akash-brain"


@patch("akash_core.github_brain.ensure_user_brain_repo", return_value="https://github.com/me/akash-brain")
@patch("akash_core.github_brain.get_gh_user", return_value="me")
def test_resolve_foreign_brain_creates_own(mock_user, mock_ensure):
    url = gb.resolve_brain_url("https://github.com/other/akash-brain")
    assert url == "https://github.com/me/akash-brain"
    mock_ensure.assert_called_once()
