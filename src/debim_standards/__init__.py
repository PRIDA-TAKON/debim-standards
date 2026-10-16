"""
debim-standards: Open Data Standards, Human Scale Anthropometrics, Building Codes, and Material Catalogs for debim.
"""

from .models import (
    ClearanceEnvelope,
    Dimensions3D,
    FurnitureStandard,
    HumanScaleCatalog,
)

__version__ = "0.1.0"

__all__ = [
    "ClearanceEnvelope",
    "Dimensions3D",
    "FurnitureStandard",
    "HumanScaleCatalog",
    "__version__",
]
