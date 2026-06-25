from akash_core.nav_map import fit_skills_for_task, register_chunks
import yaml


def test_register_chunks_and_fit(tmp_path):
    brain = tmp_path / "brain"
    (brain / "skills").mkdir(parents=True)
    register_chunks(
        brain,
        [
            {"id": "gas-dispatch", "tags": ["gas", "dispatch"], "project": "apps-script", "paths": ["a.gs"]},
            {"id": "streamlit-bi", "tags": ["streamlit", "bi"], "project": "streamlit-dashboard", "paths": ["app.py"]},
        ],
    )
    nav = yaml.safe_load((brain / "skills" / "NAV.yaml").read_text())
    assert len(nav["chunks"]) == 2
    assert len(nav["sets"]) >= 2
    ids = fit_skills_for_task(brain, "нужна рассылка gas dispatch")
    assert "gas-dispatch" in ids
