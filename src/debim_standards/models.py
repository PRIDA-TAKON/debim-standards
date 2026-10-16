"""
Pydantic data models for architectural anthropometrics and human scale standards.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class RemediationDirective(BaseModel):
    """
    Directive recommending architectural remediation actions when a rule clause is violated.
    """
    message_th: str = Field(..., description="Remediation guidance in Thai")
    message_en: str = Field(..., description="Remediation guidance in English")
    suggested_action: Optional[str] = Field(None, description="Suggested action code or parameter fix")


class EvaluationMetric(BaseModel):
    """
    Specific metric/threshold evaluation rule for a regulation clause.
    """
    metric_id: str = Field(..., description="Unique metric identifier e.g., METRIC-STAIR-RISER")
    name: str = Field(..., description="Metric description")
    parameter: str = Field(..., description="Target parameter to evaluate e.g., riser_height, clear_height")
    unit: str = Field(..., description="Unit of measurement e.g., meters, ratio, degrees")
    operator: str = Field(..., description="Comparison operator e.g., '<=', '>=', '==', '<', '>'")
    threshold: float = Field(..., description="Threshold value for evaluation")
    remediation: Optional[RemediationDirective] = Field(None, description="Remediation advice if non-compliant")

    def evaluate(self, value: float) -> bool:
        """
        Evaluates a given numeric value against threshold using operator.
        """
        if self.operator == "<=":
            return value <= self.threshold
        elif self.operator == ">=":
            return value >= self.threshold
        elif self.operator == "<":
            return value < self.threshold
        elif self.operator == ">":
            return value > self.threshold
        elif self.operator in ("==", "="):
            return value == self.threshold
        else:
            raise ValueError(f"Unsupported comparison operator: {self.operator}")


class RegulationClause(BaseModel):
    """
    A specific clause/article within a regulation ruleset.
    """
    clause_id: str = Field(..., description="Clause or article identifier e.g., CLAUSE-22, CLAUSE-51")
    title: str = Field(..., description="Clause title in Thai")
    title_en: str = Field(..., description="Clause title in English")
    description: str = Field(..., description="Summary of clause requirement")
    reference: str = Field(..., description="Legal reference e.g. Ministerial Regulation No. 55 Clause 22")
    metrics: List[EvaluationMetric] = Field(default_factory=list, description="Evaluation metrics for this clause")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")


class RegulationRuleset(BaseModel):
    """
    Comprehensive legal ruleset catalog containing multiple regulation clauses.
    """
    schema_version: str = Field(..., alias="schema", description="Schema identifier e.g., debim-standards/regulation/v1.0")
    jurisdiction: str = Field(..., description="Jurisdiction code e.g., TH, BMA")
    regulation_id: str = Field(..., description="Unique regulation catalog identifier")
    title: str = Field(..., description="Regulation title in Thai")
    title_en: str = Field(..., description="Regulation title in English")
    description: str = Field(..., description="Description of the regulation ruleset")
    clauses: Dict[str, RegulationClause] = Field(..., description="Map of clause keys to RegulationClause models")


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


class CostBreakdown(BaseModel):
    """
    Cost breakdown for a material or labor unit according to pricing guidelines (e.g. CGD ว480).
    """
    material_price: float = Field(0.0, ge=0.0, description="Material price per unit")
    labor_price: float = Field(0.0, ge=0.0, description="Labor price per unit")
    total_price: float = Field(0.0, ge=0.0, description="Total combined price per unit")
    currency: str = Field("THB", description="Currency code (e.g., THB)")


class CarbonMetrics(BaseModel):
    """
    Embodied carbon metrics for construction materials.
    """
    embodied_carbon: float = Field(..., ge=0.0, description="Embodied carbon in kgCO2e per unit")
    unit: str = Field(..., description="Unit of measurement for embodied carbon e.g., kg, cu.m, sq.m")


class MaterialItem(BaseModel):
    """
    Standardized construction material item with pricing criteria and sustainability metrics.
    """
    id: str = Field(..., description="Unique material identifier e.g., MAT-CONCRETE-240KSC")
    name: str = Field(..., description="Material name in local language (e.g., Thai)")
    name_en: str = Field(..., description="Material name in English")
    category: str = Field(..., description="Material category e.g., structural, masonry, finish, opening, roofing")
    unit: str = Field(..., description="Base unit of measurement e.g., cu.m, kg, sq.m, m, set")
    cost: Optional[CostBreakdown] = Field(None, description="Cost breakdown (material, labor, total)")
    carbon: Optional[CarbonMetrics] = Field(None, description="Embodied carbon metrics")
    specification: Optional[str] = Field(None, description="Detailed technical specification or reference criteria")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")


class MaterialCatalog(BaseModel):
    """
    Catalog of material specifications, pricing, or carbon metrics.
    """
    schema_version: str = Field(..., alias="schema", description="Schema identifier e.g., debim-standards/material/v1.0")
    catalog_id: str = Field(..., description="Unique catalog identifier e.g., CGD-V480-MATERIALS or SUSTAINABILITY-CARBON")
    title: str = Field(..., description="Catalog title in Thai")
    title_en: str = Field(..., description="Catalog title in English")
    description: str = Field(..., description="Description of the material catalog")
    items: Dict[str, MaterialItem] = Field(..., description="Map of item keys to MaterialItem models")
