from pathlib import Path
import pytest
import yaml
from pydantic import ValidationError

from debim_standards.models import (
    ClearanceEnvelope,
    Dimensions3D,
    FurnitureStandard,
    HumanScaleCatalog,
)


STANDARDS_DIR = Path(__file__).resolve().parent.parent / "standards" / "human_scale"


def test_yaml_catalogs_exist():
    expected_catalogs = ["bedroom.yaml", "living.yaml", "dining.yaml", "sanitary.yaml", "circulation.yaml"]
    for catalog_file in expected_catalogs:
        path = STANDARDS_DIR / catalog_file
        assert path.exists(), f"Catalog file missing: {catalog_file}"


@pytest.mark.parametrize(
    "yaml_filename, expected_category, expected_item_keys",
    [
        (
            "bedroom.yaml",
            "bedroom",
            ["BED_KING_6FT", "BED_QUEEN_5FT", "BED_SINGLE_35FT", "WARDROBE_12M", "WARDROBE_18M", "WARDROBE_24M", "DRESSING_TABLE"],
        ),
        (
            "living.yaml",
            "living",
            ["SOFA_2SEAT", "SOFA_3SEAT", "SOFA_LSHAPE", "COFFEE_TABLE", "TV_CONSOLE", "ARMCHAIR"],
        ),
        (
            "dining.yaml",
            "dining",
            ["DINING_TABLE_4SEAT", "DINING_TABLE_6SEAT", "DINING_TABLE_8SEAT", "DINING_CHAIR"],
        ),
        (
            "sanitary.yaml",
            "sanitary",
            ["WATER_CLOSET", "WASHBASIN_VANITY", "SHOWER_BOX_090", "BATHTUB_STANDARD"],
        ),
        (
            "circulation.yaml",
            "circulation",
            ["CORRIDOR_SINGLE", "CORRIDOR_TWO_PERSON", "WHEELCHAIR_TURNAROUND"],
        ),
    ],
)
def test_human_scale_yaml_catalog_schema_compliance(yaml_filename, expected_category, expected_item_keys):
    filepath = STANDARDS_DIR / yaml_filename
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    catalog = HumanScaleCatalog.model_validate(data)

    assert catalog.category == expected_category
    assert catalog.schema_version == "debim-standards/human-scale/v1.0"
    for key in expected_item_keys:
        assert key in catalog.items
        item = catalog.items[key]
        assert isinstance(item, FurnitureStandard)
        assert item.dimensions.width > 0
        assert item.dimensions.depth > 0
        assert item.dimensions.height > 0
        assert item.clearance.front >= 0
        assert item.clearance.back >= 0
        assert item.clearance.left >= 0
        assert item.clearance.right >= 0
        assert item.footprint_area > 0
        assert item.total_space_area > 0
        assert len(item.reference) > 0


def test_invalid_dimensions_validation():
    with pytest.raises(ValidationError):
        Dimensions3D(width=0.0, depth=1.0, height=1.0)

    with pytest.raises(ValidationError):
        Dimensions3D(width=1.0, depth=-0.5, height=1.0)


def test_invalid_clearance_validation():
    with pytest.raises(ValidationError):
        ClearanceEnvelope(front=-0.1, back=0.0, left=0.0, right=0.0)
