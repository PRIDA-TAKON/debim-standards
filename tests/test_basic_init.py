"""
Basic sanity tests for debim-standards package initialization and roadmap integrity.
"""

import json
from pathlib import Path


def test_package_init():
    import debim_standards
    assert debim_standards.__version__ == "0.1.0"


def test_roadmap_config_validity():
    repo_root = Path(__file__).resolve().parent.parent
    roadmap_file = repo_root / "tools" / "roadmap_standards.json"
    assert roadmap_file.exists(), "roadmap_standards.json must exist"

    with open(roadmap_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 5, "Roadmap should have 5 waves configured"

    for wave in data:
        assert "wave" in wave
        assert "issue_key" in wave
        assert "match_keywords" in wave
        if wave.get("is_final_wave"):
            assert wave.get("next_issue") is None
        else:
            assert "next_issue" in wave
            assert "title" in wave["next_issue"]
            assert "body" in wave["next_issue"]
