from pathlib import Path

from akash_core.hooks_gate import pack_ready, prepare_gate, session_start


def test_pack_ready(tmp_path):
    session = tmp_path / "session.json"
    assert not pack_ready(session)
    session.write_text('{"task": "x", "skills": ["a"]}', encoding="utf-8")
    assert pack_ready(session)


def test_gate_denies_read_without_pack(tmp_path, monkeypatch):
    monkeypatch.setattr("akash_core.hooks_gate.CONFIG", tmp_path / "c")
    monkeypatch.setattr("akash_core.hooks_gate.SESSION", tmp_path / "s")
    (tmp_path / "c").write_text("x", encoding="utf-8")
    out = prepare_gate({"tool_name": "Read", "tool_input": {}})
    assert out["permission"] == "deny"


def test_gate_allows_akash_shell(tmp_path, monkeypatch):
    monkeypatch.setattr("akash_core.hooks_gate.CONFIG", tmp_path / "c")
    (tmp_path / "c").write_text("x", encoding="utf-8")
    out = prepare_gate(
        {"tool_name": "Shell", "tool_input": {"command": "python3 -m akash_core.cli prepare foo"}}
    )
    assert out["permission"] == "allow"


def test_session_start_no_config(tmp_path, monkeypatch):
    monkeypatch.setattr("akash_core.hooks_gate.CONFIG", tmp_path / "missing")
    monkeypatch.setattr("akash_core.hooks_gate.META", tmp_path / "meta")
    monkeypatch.setattr("akash_core.hooks_gate.SESSION", tmp_path / "sess")
    assert session_start({"session_id": "abc"}) == {}
