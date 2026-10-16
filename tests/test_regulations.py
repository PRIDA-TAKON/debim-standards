from pathlib import Path
import pytest
import yaml
from pydantic import ValidationError

from debim_standards.models import (
    EvaluationMetric,
    RegulationClause,
    RegulationRuleset,
    RemediationDirective,
)


REGULATIONS_DIR = Path(__file__).resolve().parent.parent / "standards" / "regulations" / "th"


def test_yaml_regulation_files_exist():
    expected_files = ["ministerial_reg_55.yaml", "setbacks.yaml"]
    for filename in expected_files:
        path = REGULATIONS_DIR / filename
        assert path.exists(), f"Regulation file missing: {filename}"


def test_ministerial_reg_55_yaml_parsing():
    filepath = REGULATIONS_DIR / "ministerial_reg_55.yaml"
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    ruleset = RegulationRuleset.model_validate(data)

    assert ruleset.schema_version == "debim-standards/regulation/v1.0"
    assert ruleset.jurisdiction == "TH"
    assert ruleset.regulation_id == "TH-MR55-2543"

    # Verify Clause 51 (Light and Ventilation >= 10%)
    assert "CLAUSE_51_LIGHT_VENTILATION" in ruleset.clauses
    c51 = ruleset.clauses["CLAUSE_51_LIGHT_VENTILATION"]
    assert c51.clause_id == "CLAUSE-51"
    assert len(c51.metrics) == 1
    m51 = c51.metrics[0]
    assert m51.metric_id == "METRIC-LIGHT-VENT-RATIO"
    assert m51.parameter == "opening_area_ratio"
    assert m51.threshold == 0.10
    assert m51.operator == ">="
    assert m51.evaluate(0.12) is True
    assert m51.evaluate(0.10) is True
    assert m51.evaluate(0.08) is False
    assert m51.remediation is not None
    assert "10%" in m51.remediation.message_th

    # Verify Clause 22 (Stairs)
    assert "CLAUSE_22_STAIR_DESIGN" in ruleset.clauses
    c22 = ruleset.clauses["CLAUSE_22_STAIR_DESIGN"]
    assert c22.clause_id == "CLAUSE-22"
    metric_map = {m.metric_id: m for m in c22.metrics}

    riser = metric_map["METRIC-STAIR-RISER"]
    assert riser.operator == "<="
    assert riser.threshold == 0.20
    assert riser.evaluate(0.18) is True
    assert riser.evaluate(0.20) is True
    assert riser.evaluate(0.21) is False

    tread = metric_map["METRIC-STAIR-TREAD"]
    assert tread.operator == ">="
    assert tread.threshold == 0.22
    assert tread.evaluate(0.25) is True
    assert tread.evaluate(0.22) is True
    assert tread.evaluate(0.20) is False

    width = metric_map["METRIC-STAIR-CLEAR-WIDTH"]
    assert width.operator == ">="
    assert width.threshold == 0.90
    assert width.evaluate(1.00) is True
    assert width.evaluate(0.90) is True
    assert width.evaluate(0.85) is False

    headroom = metric_map["METRIC-STAIR-HEADROOM"]
    assert headroom.operator == ">="
    assert headroom.threshold == 2.00
    assert headroom.evaluate(2.10) is True
    assert headroom.evaluate(2.00) is True
    assert headroom.evaluate(1.90) is False

    # Verify Clause 33 (Clear Height)
    assert "CLAUSE_33_ROOM_CLEAR_HEIGHT" in ruleset.clauses
    c33 = ruleset.clauses["CLAUSE_33_ROOM_CLEAR_HEIGHT"]
    c33_map = {m.metric_id: m for m in c33.metrics}

    habitable = c33_map["METRIC-HABITABLE-CLEAR-HEIGHT"]
    assert habitable.threshold == 2.60
    assert habitable.evaluate(2.80) is True
    assert habitable.evaluate(2.60) is True
    assert habitable.evaluate(2.40) is False

    bathroom = c33_map["METRIC-BATHROOM-CLEAR-HEIGHT"]
    assert bathroom.threshold == 2.00
    assert bathroom.evaluate(2.20) is True
    assert bathroom.evaluate(2.00) is True
    assert bathroom.evaluate(1.80) is False

    # Verify Clause 40 (Wet Area Bathroom Drop Elevation)
    assert "CLAUSE_40_WET_AREA_FLOOR_DROP" in ruleset.clauses
    c40 = ruleset.clauses["CLAUSE_40_WET_AREA_FLOOR_DROP"]
    m40 = c40.metrics[0]
    assert m40.metric_id == "METRIC-BATHROOM-DROP-ELEVATION"
    assert m40.parameter == "drop_elevation"
    assert m40.operator == "<="
    assert m40.threshold == -0.10
    # drop elevation of -0.10m or lower (-0.12m) is compliant (step-down of >= 0.10m)
    assert m40.evaluate(-0.12) is True
    assert m40.evaluate(-0.10) is True
    # drop elevation of -0.05m is not enough step-down (non-compliant)
    assert m40.evaluate(-0.05) is False


def test_setbacks_yaml_parsing():
    filepath = REGULATIONS_DIR / "setbacks.yaml"
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    ruleset = RegulationRuleset.model_validate(data)

    assert ruleset.schema_version == "debim-standards/regulation/v1.0"
    assert ruleset.jurisdiction == "TH"
    assert ruleset.regulation_id == "TH-SETBACKS-2543"

    # Blank wall setback (>= 0.50m)
    blank_clause = ruleset.clauses["CLAUSE_PROPERTY_SETBACK_BLANK_WALL"]
    m_blank = blank_clause.metrics[0]
    assert m_blank.threshold == 0.50
    assert m_blank.evaluate(0.60) is True
    assert m_blank.evaluate(0.50) is True
    assert m_blank.evaluate(0.40) is False

    # Opening/Balcony wall setback (>= 2.00m)
    opening_clause = ruleset.clauses["CLAUSE_PROPERTY_SETBACK_OPENING"]
    m_opening = opening_clause.metrics[0]
    assert m_opening.threshold == 2.00
    assert m_opening.evaluate(2.50) is True
    assert m_opening.evaluate(2.00) is True
    assert m_opening.evaluate(1.50) is False


def test_evaluation_metric_operators():
    m_lt = EvaluationMetric(
        metric_id="M1",
        name="test",
        parameter="p",
        unit="m",
        operator="<",
        threshold=5.0,
    )
    assert m_lt.evaluate(4.0) is True
    assert m_lt.evaluate(5.0) is False

    m_gt = EvaluationMetric(
        metric_id="M2",
        name="test",
        parameter="p",
        unit="m",
        operator=">",
        threshold=5.0,
    )
    assert m_gt.evaluate(6.0) is True
    assert m_gt.evaluate(5.0) is False

    m_eq = EvaluationMetric(
        metric_id="M3",
        name="test",
        parameter="p",
        unit="m",
        operator="==",
        threshold=5.0,
    )
    assert m_eq.evaluate(5.0) is True
    assert m_eq.evaluate(5.1) is False

    m_invalid = EvaluationMetric(
        metric_id="M4",
        name="test",
        parameter="p",
        unit="m",
        operator="INVALID",
        threshold=5.0,
    )
    with pytest.raises(ValueError, match="Unsupported comparison operator"):
        m_invalid.evaluate(5.0)
