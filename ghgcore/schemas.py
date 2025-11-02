"""
Pydantic schemas for API validation and data transfer.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum


class ScopeEnum(int, Enum):
    """GHG Protocol Scopes."""
    SCOPE_1 = 1
    SCOPE_2 = 2
    SCOPE_3 = 3


class GWPSetEnum(str, Enum):
    """IPCC Assessment Report versions."""
    AR5 = "AR5"
    AR6 = "AR6"


class ElectricityMethodEnum(str, Enum):
    """Electricity accounting method."""
    LOCATION = "location"
    MARKET = "market"
    BOTH = "both"


class ConsolidationApproachEnum(str, Enum):
    """GHG Protocol consolidation approaches."""
    EQUITY_SHARE = "equity_share"
    OPERATIONAL_CONTROL = "operational_control"
    FINANCIAL_CONTROL = "financial_control"


# Organization schemas
class OrganizationCreate(BaseModel):
    """Schema for creating an organization."""
    name: str
    country: str
    sector: str
    base_year: int
    period_start: date
    period_end: date
    gwp_set: GWPSetEnum = GWPSetEnum.AR5
    electricity_method: ElectricityMethodEnum = ElectricityMethodEnum.LOCATION
    consolidation_approach: ConsolidationApproachEnum = ConsolidationApproachEnum.OPERATIONAL_CONTROL

    @validator('period_end')
    def end_after_start(cls, v, values):
        if 'period_start' in values and v < values['period_start']:
            raise ValueError('period_end must be after period_start')
        return v


class OrganizationRead(BaseModel):
    """Schema for reading organization data."""
    id: int
    name: str
    country: str
    sector: str
    base_year: int
    period_start: date
    period_end: date
    gwp_set: str
    electricity_method: str
    consolidation_approach: str
    created_at: datetime

    class Config:
        from_attributes = True


# Facility schemas
class FacilityCreate(BaseModel):
    """Schema for creating a facility."""
    org_id: int
    name: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    grid_region: Optional[str] = None
    consolidation_method: str = "100%"


class FacilityRead(BaseModel):
    """Schema for reading facility data."""
    id: int
    org_id: int
    name: str
    lat: Optional[float]
    lon: Optional[float]
    grid_region: Optional[str]
    consolidation_method: str

    class Config:
        from_attributes = True


# Activity schemas
class ActivityCreate(BaseModel):
    """Schema for creating an activity."""
    facility_id: int
    source_id: int
    activity_type: str
    activity_date: date
    method_key: str
    units_json: Dict[str, Any]
    data_json: Dict[str, Any] = {}
    evidence_note: Optional[str] = None


class ActivityRead(BaseModel):
    """Schema for reading activity data."""
    id: int
    facility_id: int
    source_id: int
    activity_type: str
    activity_date: date
    method_key: str
    units_json: Dict[str, Any]
    data_json: Dict[str, Any]
    evidence_note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Emission Factor schemas
class EmissionFactorCreate(BaseModel):
    """Schema for creating an emission factor."""
    scope: int
    subcategory: str
    activity_code: str
    activity_name: str
    gas: str
    factor_value: float
    factor_unit: str
    basis: str = "NA"
    oxidation_frac: float = 1.0
    fuel_state: str = "NA"
    source_authority: str
    source_doc: str
    source_table: Optional[str] = None
    source_year: int
    geography: str = "Global"
    region_code: Optional[str] = None
    market_or_location: str = "NA"
    technology: Optional[str] = None
    uncertainty_pct: Optional[float] = None
    valid_from: date
    valid_to: Optional[date] = None
    citation: Optional[str] = None
    method_equation_ref: Optional[str] = None
    notes: Optional[str] = None

    @validator('factor_value')
    def value_positive(cls, v):
        if v <= 0:
            raise ValueError('factor_value must be positive')
        return v

    @validator('scope')
    def valid_scope(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError('scope must be 1, 2, or 3')
        return v


class EmissionFactorRead(BaseModel):
    """Schema for reading emission factor data."""
    id: int
    scope: int
    subcategory: str
    activity_code: str
    activity_name: str
    gas: str
    factor_value: float
    factor_unit: str
    basis: str
    oxidation_frac: float
    fuel_state: str
    source_authority: str
    source_doc: str
    source_table: Optional[str]
    source_year: int
    geography: str
    region_code: Optional[str]
    market_or_location: str
    technology: Optional[str]
    uncertainty_pct: Optional[float]
    valid_from: date
    valid_to: Optional[date]
    citation: Optional[str]
    method_equation_ref: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Calculation result schemas
class CalculationInput(BaseModel):
    """Input for calculation."""
    activity_id: int
    emission_factor_id: int
    method_key: str


class EmissionResult(BaseModel):
    """Single gas emission result."""
    gas: str
    mass_kg: float
    co2e_kg: float
    gwp_value: float


class CalculationResult(BaseModel):
    """Complete calculation result."""
    calculation_id: int
    activity_id: int
    emissions: List[EmissionResult]
    total_co2e_kg: float
    timestamp: datetime
    method_key: str


# Report generation schemas
class ReportConfig(BaseModel):
    """Configuration for report generation."""
    org_id: int
    include_charts: bool = True
    include_evidence_manifest: bool = True
    format: str = "html"  # html, pdf, excel


class ReportSectionUpdate(BaseModel):
    """Update text for a report section."""
    org_id: int
    clause_key: str
    markdown_text: str
