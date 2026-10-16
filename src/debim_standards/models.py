"""
Pydantic data models for architectural anthropometrics and human scale standards.
"""

from typing import Dict, List
from pydantic import BaseModel, Field


class ClearanceEnvelope(BaseModel):
    """
    Clearance envelope margins around a furniture or spatial element (in meters).
    All clearance dimensions must be non-negative (>= 0.0).
    """
    front: float = Field(..., ge=0.0, description="Front clearance distance in meters")
    back: float = Field(..., ge=0.0, description="Back clearance distance in meters")
    left: float = Field(..., ge=0.0, description="Left side clearance distance in meters")
    right: float = Field(..., ge=0.0, description="Right side clearance distance in meters")


class Dimensions3D(BaseModel):
    """
    3D physical dimensions of an element (width x depth x height in meters).
    All dimensions must be strictly positive (> 0.0).
    """
    width: float = Field(..., gt=0.0, description="Width (X-axis) in meters")
    depth: float = Field(..., gt=0.0, description="Depth (Y-axis) in meters")
    height: float = Field(..., gt=0.0, description="Height (Z-axis) in meters")


class FurnitureStandard(BaseModel):
    """
    Standardized human scale furniture item or spatial activity envelope.
    """
    id: str = Field(..., description="Unique standard identifier e.g., FUR-BED-KING-6FT")
    name: str = Field(..., description="Item name in local language (e.g., Thai)")
    name_en: str = Field(..., description="Item name in English")
    category: str = Field(..., description="Furniture category e.g., bedroom, living, sanitary")
    dimensions: Dimensions3D = Field(..., description="3D physical dimensions (width, depth, height)")
    clearance: ClearanceEnvelope = Field(..., description="Usage clearance margins (front, back, left, right)")
    reference: str = Field(..., description="Literature or standard citation e.g., Neufert 4th Ed, Panero & Zelnik")
    footprint_area: float = Field(..., gt=0.0, description="Physical footprint area in sq.m (width * depth)")
    total_space_area: float = Field(..., gt=0.0, description="Total space area including clearances in sq.m")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")


class HumanScaleCatalog(BaseModel):
    """
    Catalog of human scale furniture standards for a given spatial domain.
    """
    schema_version: str = Field(..., alias="schema", description="Schema identifier e.g., debim-standards/human-scale/v1.0")
    category: str = Field(..., description="Space category e.g., bedroom, living, dining")
    description: str = Field(..., description="Brief description of the catalog domain")
    items: Dict[str, FurnitureStandard] = Field(..., description="Map of item keys to FurnitureStandard models")
