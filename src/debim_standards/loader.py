"""
High-level querying APIs for debim-standards SDK.
Provides unified access to furniture scale standards, building codes/regulations,
and material catalog specifications/pricing.
"""

from typing import List, Optional
from .cache import StandardsCache
from .models import FurnitureStandard, MaterialItem, RegulationClause

_DEFAULT_CACHE = StandardsCache()


def _get_active_cache(cache: Optional[StandardsCache] = None) -> StandardsCache:
    return cache if cache is not None else _DEFAULT_CACHE


def get_furniture(
    ref_id: str, cache: Optional[StandardsCache] = None
) -> Optional[FurnitureStandard]:
    """
    Retrieves a FurnitureStandard by its reference key or ID.
    Supports catalog key (e.g., 'BED_KING_6FT'), item ID (e.g., 'FUR-BED-KING-6FT'),
    and dot-notation path (e.g., 'standards.human_scale.bedroom.BED_KING_6FT').

    Returns None if the furniture standard is not found.
    """
    if not ref_id:
        return None

    active_cache = _get_active_cache(cache)
    data = active_cache.get_data().get("human_scale", {})

    # Try direct lookup
    item_dict = data.get(ref_id)

    if item_dict is None:
        # Try stripped ref_id
        clean_ref = ref_id
        for prefix in ("standards.human_scale.", "human_scale.", "standards."):
            if clean_ref.startswith(prefix):
                clean_ref = clean_ref[len(prefix) :]
                break

        # Check in stripped key or split parts
        item_dict = data.get(clean_ref)
        if item_dict is None and "." in clean_ref:
            key_part = clean_ref.split(".")[-1]
            item_dict = data.get(key_part)

    if item_dict is None:
        item_dict = data.get(ref_id.lower())

    if item_dict is None:
        return None

    try:
        return FurnitureStandard.model_validate(item_dict)
    except Exception:
        return None


def get_regulations(
    jurisdiction: str = "TH", cache: Optional[StandardsCache] = None
) -> List[RegulationClause]:
    """
    Retrieves all regulation clauses for a given jurisdiction code (default: 'TH').
    Returns an empty list if no clauses match.
    """
    if not jurisdiction:
        return []

    active_cache = _get_active_cache(cache)
    reg_data = active_cache.get_data().get("regulations", {})
    clause_list = reg_data.get(jurisdiction.upper(), [])

    results: List[RegulationClause] = []
    for c_dict in clause_list:
        try:
            results.append(RegulationClause.model_validate(c_dict))
        except Exception:
            continue

    return results


def get_material_price(
    material_id: str, cache: Optional[StandardsCache] = None
) -> Optional[MaterialItem]:
    """
    Retrieves a MaterialItem containing cost breakdown and carbon metrics by material key or ID.
    (e.g., 'MAT-CONCRETE-240-CUBE' or 'CONCRETE_240_CUBE').

    Returns None if the material is not found.
    """
    if not material_id:
        return None

    active_cache = _get_active_cache(cache)
    mat_data = active_cache.get_data().get("materials", {})

    item_dict = mat_data.get(material_id)
    if item_dict is None:
        item_dict = mat_data.get(material_id.lower())

    if item_dict is None:
        return None

    try:
        return MaterialItem.model_validate(item_dict)
    except Exception:
        return None
