import os
import time
from pathlib import Path
import pytest
from unittest.mock import patch

from debim_standards import (
    FurnitureStandard,
    MaterialItem,
    RegulationClause,
    StandardsCache,
    get_furniture,
    get_material_price,
    get_regulations,
)


def test_get_furniture_queries():
    # 1. Query by item key
    bed_key = get_furniture("BED_KING_6FT")
    assert bed_key is not None
    assert isinstance(bed_key, FurnitureStandard)
    assert bed_key.id == "FUR-BED-KING-6FT"
    assert bed_key.dimensions.width == 1.80
    assert bed_key.dimensions.depth == 2.00
    assert bed_key.clearance.front == 0.80
    assert bed_key.clearance.left == 0.60
    assert bed_key.clearance.right == 0.60

    # 2. Query by item ID
    bed_id = get_furniture("FUR-BED-KING-6FT")
    assert bed_id is not None
    assert bed_id.id == "FUR-BED-KING-6FT"

    # 3. Query by dot notation path
    bed_dot = get_furniture("standards.human_scale.bedroom.BED_KING_6FT")
    assert bed_dot is not None
    assert bed_dot.id == "FUR-BED-KING-6FT"

    # 4. Query by lowercase key
    bed_lower = get_furniture("bed_king_6ft")
    assert bed_lower is not None
    assert bed_lower.id == "FUR-BED-KING-6FT"

    # 5. Non-existent reference
    assert get_furniture("NON_EXISTENT_FURNITURE_XYZ") is None
    assert get_furniture("") is None


def test_get_regulations_queries():
    # 1. Query Thailand regulations
    clauses = get_regulations("TH")
    assert isinstance(clauses, list)
    assert len(clauses) > 0

    clause_ids = [c.clause_id for c in clauses]
    assert "CLAUSE-51" in clause_ids
    assert "CLAUSE-22" in clause_ids
    assert "CLAUSE-33" in clause_ids

    # Verify metric evaluation on Clause 51 (Ventilation)
    c51 = next(c for c in clauses if c.clause_id == "CLAUSE-51")
    assert len(c51.metrics) == 1
    m51 = c51.metrics[0]
    assert m51.evaluate(0.15) is True
    assert m51.evaluate(0.05) is False

    # 2. Case-insensitive jurisdiction
    clauses_lower = get_regulations("th")
    assert len(clauses_lower) == len(clauses)

    # 3. Non-existent jurisdiction
    assert get_regulations("NON_EXISTENT_JURISDICTION") == []
    assert get_regulations("") == []


def test_get_material_price_queries():
    # 1. Query by item ID
    mat_id = get_material_price("MAT-CONCRETE-240-CUBE")
    assert mat_id is not None
    assert isinstance(mat_id, MaterialItem)
    assert mat_id.name == "คอนกรีตโครงสร้าง 240 ksc (Cube)"
    assert mat_id.cost is not None
    assert mat_id.cost.material_price == 1850.0
    assert mat_id.cost.labor_price == 440.0
    assert mat_id.cost.total_price == 2290.0

    # Merged carbon metric from sustainability catalog
    assert mat_id.carbon is not None
    assert mat_id.carbon.embodied_carbon == 320.0

    # 2. Query by item key
    mat_key = get_material_price("CONCRETE_240_CUBE")
    assert mat_key is not None
    assert mat_key.id == "MAT-CONCRETE-240-CUBE"

    # 3. Query by lowercase key
    mat_lower = get_material_price("concrete_240_cube")
    assert mat_lower is not None

    # 4. Non-existent material
    assert get_material_price("MAT_NON_EXISTENT_ABC") is None
    assert get_material_price("") is None


def test_cache_lifecycle_and_ttl(tmp_path):
    cache_dir = tmp_path / "test_debim_cache"
    custom_cache = StandardsCache(cache_dir=cache_dir, ttl_seconds=100)

    # Initially cache file does not exist
    assert not custom_cache.cache_file.exists()
    assert not custom_cache.is_cache_valid()

    # Query using custom cache Populates cache file
    item = get_furniture("BED_KING_6FT", cache=custom_cache)
    assert item is not None
    assert custom_cache.cache_file.exists()
    assert custom_cache.is_cache_valid()

    # Verify cached data read
    cached_data = custom_cache.load_from_cache()
    assert cached_data is not None
    assert "human_scale" in cached_data

    # Test TTL Expiration (set timestamp back 200 seconds)
    with patch("time.time", return_value=time.time() + 200):
        assert not custom_cache.is_cache_valid()
        # Loading from cache returns None when expired
        assert custom_cache.load_from_cache() is None

    # Test clear_cache
    assert custom_cache.clear_cache() is True
    assert not custom_cache.cache_file.exists()


def test_air_gapped_offline_fallback(tmp_path):
    # Pass a non-writable cache path or directory that fails to save
    invalid_dir = tmp_path / "non_existent_sub_dir"
    cache = StandardsCache(cache_dir=invalid_dir)

    # Mock save_to_cache to simulate read-only / unwriteable disk
    with patch.object(cache, "save_to_cache", return_value=False):
        data = cache.get_data()
        assert "human_scale" in data
        assert "regulations" in data
        assert "materials" in data

    # Verify loader functions still succeed seamlessly
    fur = get_furniture("SOFA_2SEAT", cache=cache)
    assert fur is not None
    assert fur.id == "FUR-SOFA-2SEAT"


def test_zero_network_dependency(monkeypatch):
    # Disable network socket connection attempts
    def guard_socket(*args, **kwargs):
        raise RuntimeError("Network socket access attempted in zero-network SDK!")

    monkeypatch.setattr("socket.socket", guard_socket)

    # Perform queries and verify no network requests are attempted
    fur = get_furniture("BED_QUEEN_5FT")
    assert fur is not None

    regs = get_regulations("TH")
    assert len(regs) > 0

    mat = get_material_price("REBAR_RB9")
    assert mat is not None
