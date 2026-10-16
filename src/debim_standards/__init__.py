"""
debim-standards: Open Data Standards, Human Scale Anthropometrics, Building Codes, and Material Catalogs for debim.
"""

from .cache import StandardsCache
from .loader import get_furniture, get_material_price, get_regulations
from .models import (
    CarbonMetrics,
    ClearanceEnvelope,
    CostBreakdown,
    Dimensions3D,
    EvaluationMetric,
    FurnitureStandard,
    HumanScaleCatalog,
    MaterialCatalog,
    MaterialItem,
    RegulationClause,
    RegulationRuleset,
    RemediationDirective,
)

__version__ = "0.1.0"

__all__ = [
    "CarbonMetrics",
    "ClearanceEnvelope",
    "CostBreakdown",
    "Dimensions3D",
    "EvaluationMetric",
    "FurnitureStandard",
    "HumanScaleCatalog",
    "MaterialCatalog",
    "MaterialItem",
    "RegulationClause",
    "RegulationRuleset",
    "RemediationDirective",
    "StandardsCache",
    "get_furniture",
    "get_material_price",
    "get_regulations",
    "__version__",
]
