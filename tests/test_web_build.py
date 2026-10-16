"""
tests/test_web_build.py

Unit tests verifying that tools/build_web_data.py correctly compiles
all source YAML standards into docs/data.json without loss or mismatch.
"""

import json
from pathlib import Path
import pytest
import yaml

from tools.build_web_data import build_web_data

ROOT_DIR = Path(__file__).resolve().parent.parent
STANDARDS_DIR = ROOT_DIR / "standards"
DATA_JSON = ROOT_DIR / "docs" / "data.json"


def test_build_web_data_execution():
    """Verify build_web_data executes successfully and creates docs/data.json."""
    data = build_web_data()
    assert DATA_JSON.exists(), "docs/data.json should exist after build_web_data execution"
    assert "human_scale" in data
    assert "regulations" in data
    assert "materials" in data


def test_data_json_matches_human_scale_yaml():
    """Verify human_scale in docs/data.json matches source YAML files."""
    with open(DATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    json_items = {item["id"]: item for item in data["human_scale"]}

    # Collect source YAML items
    source_items = {}
    for yaml_path in (STANDARDS_DIR / "human_scale").glob("*.yaml"):
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f) or {}
            for key, val in content.get("items", {}).items():
                source_items[val["id"]] = val

    assert len(json_items) == len(source_items), "All human scale items from YAML must be in data.json"

    for item_id, source_val in source_items.items():
        assert item_id in json_items, f"Item {item_id} missing from docs/data.json"
        target = json_items[item_id]
        assert target["name"] == source_val["name"]
        assert target["name_en"] == source_val["name_en"]
        assert target["dimensions"] == source_val["dimensions"]
        assert target["clearance"] == source_val["clearance"]
        assert target["footprint_area"] == pytest.approx(source_val["footprint_area"])
        assert target["total_space_area"] == pytest.approx(source_val["total_space_area"])


def test_data_json_matches_regulations_yaml():
    """Verify regulations in docs/data.json match source YAML files."""
    with open(DATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    json_rulesets = {r["regulation_id"]: r for r in data["regulations"]}

    yaml_files = list((STANDARDS_DIR / "regulations").glob("**/*.yaml"))
    assert len(yaml_files) > 0

    for yaml_path in yaml_files:
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f) or {}
            reg_id = content["regulation_id"]
            assert reg_id in json_rulesets
            json_clauses = {c["clause_id"]: c for c in json_rulesets[reg_id]["clauses"]}

            for c_key, c_val in content.get("clauses", {}).items():
                c_id = c_val["clause_id"]
                assert c_id in json_clauses
                json_clause = json_clauses[c_id]
                assert json_clause["title"] == c_val["title"]
                assert len(json_clause["metrics"]) == len(c_val["metrics"])


def test_data_json_matches_materials_yaml():
    """Verify materials in docs/data.json match source YAML files."""
    with open(DATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    json_materials = {m["id"]: m for m in data["materials"]}

    cgd_path = STANDARDS_DIR / "materials" / "cgd_v480.yaml"
    if cgd_path.exists():
        with open(cgd_path, "r", encoding="utf-8") as f:
            cgd_content = yaml.safe_load(f) or {}
            for item_key, item_val in cgd_content.get("items", {}).items():
                m_id = item_val["id"]
                assert m_id in json_materials
                assert json_materials[m_id]["cost"]["total_price"] == item_val["cost"]["total_price"]

    sust_path = STANDARDS_DIR / "materials" / "sustainability.yaml"
    if sust_path.exists():
        with open(sust_path, "r", encoding="utf-8") as f:
            sust_content = yaml.safe_load(f) or {}
            for item_key, item_val in sust_content.get("items", {}).items():
                m_id = item_val["id"]
                assert m_id in json_materials
                assert json_materials[m_id]["carbon"]["embodied_carbon"] == item_val["carbon"]["embodied_carbon"]
