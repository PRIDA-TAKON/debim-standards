from pathlib import Path
import pytest
import yaml
from pydantic import ValidationError

from debim_standards.models import (
    CarbonMetrics,
    CostBreakdown,
    MaterialCatalog,
    MaterialItem,
)


MATERIALS_DIR = Path(__file__).resolve().parent.parent / "standards" / "materials"


def test_yaml_material_files_exist():
    expected_files = ["cgd_v480.yaml", "sustainability.yaml"]
    for filename in expected_files:
        path = MATERIALS_DIR / filename
        assert path.exists(), f"Material catalog file missing: {filename}"


def test_cgd_v480_yaml_parsing():
    filepath = MATERIALS_DIR / "cgd_v480.yaml"
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    catalog = MaterialCatalog.model_validate(data)

    assert catalog.schema_version == "debim-standards/material/v1.0"
    assert catalog.catalog_id == "CGD-V480-MATERIALS"

    # Required CGD ว480 standard items
    required_keys = [
        # Structural Concrete
        "CONCRETE_240_CUBE",
        "CONCRETE_280_CUBE",
        # Rebar
        "REBAR_RB9",
        "REBAR_DB12",
        "REBAR_DB16",
        "REBAR_DB20",
        "REBAR_DB25",
        # Formwork
        "FORMWORK_WOODEN",
        "FORMWORK_STEEL_PROPS",
        # Masonry & Finishes
        "MASONRY_AAC_75MM",
        "MASONRY_CLAY_BRICK",
        "FINISH_CERAMIC_TILE",
        "FINISH_GRANITE_TILE",
        "FINISH_WOOD_PARQUET",
        # Openings & Roofing
        "OPENING_ALUMINUM_GLASS_DOOR",
        "OPENING_ALUMINUM_GLASS_WINDOW",
        "ROOFING_CPAC_MONIER",
        "ROOFING_METAL_SHEET_PU",
    ]

    for key in required_keys:
        assert key in catalog.items, f"Missing required CGD v480 key: {key}"
        item = catalog.items[key]
        assert isinstance(item, MaterialItem)
        assert item.cost is not None
        # Verify total price consistency
        assert pytest.approx(item.cost.total_price) == item.cost.material_price + item.cost.labor_price
        assert item.cost.currency == "THB"
        assert len(item.name) > 0
        assert len(item.name_en) > 0


def test_sustainability_yaml_parsing():
    filepath = MATERIALS_DIR / "sustainability.yaml"
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    catalog = MaterialCatalog.model_validate(data)

    assert catalog.schema_version == "debim-standards/material/v1.0"
    assert catalog.catalog_id == "SUSTAINABILITY-CARBON-MATERIALS"

    required_keys = [
        "CONCRETE_240_CUBE",
        "CONCRETE_280_CUBE",
        "REBAR_STEEL",
        "FORMWORK_WOODEN",
        "FORMWORK_STEEL_PROPS",
        "MASONRY_AAC_75MM",
        "MASONRY_CLAY_BRICK",
        "FINISH_CERAMIC_TILE",
        "FINISH_GRANITE_TILE",
        "FINISH_WOOD_PARQUET",
        "OPENING_ALUMINUM_GLASS_DOOR",
        "OPENING_ALUMINUM_GLASS_WINDOW",
        "ROOFING_CPAC_MONIER",
        "ROOFING_METAL_SHEET_PU",
    ]

    for key in required_keys:
        assert key in catalog.items, f"Missing required sustainability carbon key: {key}"
        item = catalog.items[key]
        assert isinstance(item, MaterialItem)
        assert item.carbon is not None
        assert item.carbon.embodied_carbon >= 0.0
        assert item.carbon.unit == item.unit


def test_invalid_cost_breakdown_validation():
    with pytest.raises(ValidationError):
        CostBreakdown(material_price=-10.0, labor_price=5.0, total_price=0.0)

    with pytest.raises(ValidationError):
        CostBreakdown(material_price=10.0, labor_price=-5.0, total_price=5.0)


def test_invalid_carbon_metrics_validation():
    with pytest.raises(ValidationError):
        CarbonMetrics(embodied_carbon=-1.5, unit="kg")
