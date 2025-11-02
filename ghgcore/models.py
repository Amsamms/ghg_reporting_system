"""
SQLModel ORM for GHG Inventory Database
Defines all database tables with proper relationships, indexes, and constraints.
"""

from typing import Optional, Dict, Any
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from sqlalchemy import UniqueConstraint, Index


class Organization(SQLModel, table=True):
    """Organization/Company entity with reporting configuration."""
    __tablename__ = "organizations"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    country: str
    sector: str  # e.g., "Petroleum Refining", "Upstream Oil & Gas"
    base_year: int
    period_start: date
    period_end: date
    gwp_set: str = Field(default="AR5")  # AR5 or AR6
    electricity_method: str = Field(default="location")  # location, market, or both
    consolidation_approach: str = Field(default="operational_control")  # equity_share, operational_control, financial_control
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    facilities: list["Facility"] = Relationship(back_populates="organization")
    report_sections: list["ReportSection"] = Relationship(back_populates="organization")


class Facility(SQLModel, table=True):
    """Facility/Site within an organization."""
    __tablename__ = "facilities"

    id: Optional[int] = Field(default=None, primary_key=True)
    org_id: int = Field(foreign_key="organizations.id", index=True)
    name: str = Field(index=True)
    lat: Optional[float] = None
    lon: Optional[float] = None
    grid_region: Optional[str] = None  # For electricity grid emission factors
    consolidation_method: str = Field(default="100%")  # e.g., "100%", "50%", "equity_share_35%"

    # Relationships
    organization: Organization = Relationship(back_populates="facilities")
    activities: list["Activity"] = Relationship(back_populates="facility")


class Source(SQLModel, table=True):
    """Emission source categories (Scope 1, 2, 3 subcategories)."""
    __tablename__ = "sources"

    id: Optional[int] = Field(default=None, primary_key=True)
    scope: int = Field(index=True)  # 1, 2, or 3
    subcategory: str = Field(index=True)  # e.g., "stationary_combustion", "flaring", "purchased_electricity"
    description: Optional[str] = None

    # Relationships
    activities: list["Activity"] = Relationship(back_populates="source")

    __table_args__ = (
        UniqueConstraint('scope', 'subcategory', name='uq_scope_subcategory'),
    )


class Activity(SQLModel, table=True):
    """Individual emission activity/transaction."""
    __tablename__ = "activities"

    id: Optional[int] = Field(default=None, primary_key=True)
    facility_id: int = Field(foreign_key="facilities.id", index=True)
    source_id: int = Field(foreign_key="sources.id", index=True)
    activity_type: str  # e.g., "natural_gas_combustion", "diesel_generator"
    activity_date: date = Field(index=True)
    method_key: str  # Reference to calculation method (e.g., "EPA_C1", "IPCC_Vol2_Ch2")
    units_json: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # {"quantity": 1000, "unit": "GJ"}
    data_json: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Additional activity data
    evidence_note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    facility: Facility = Relationship(back_populates="activities")
    source: Source = Relationship(back_populates="activities")
    calculations: list["Calculation"] = Relationship(back_populates="activity")
    attachments: list["Attachment"] = Relationship(back_populates="activity")


class EmissionFactor(SQLModel, table=True):
    """Canonical emission factors from various authorities."""
    __tablename__ = "emission_factors"

    id: Optional[int] = Field(default=None, primary_key=True)
    scope: int = Field(index=True)
    subcategory: str = Field(index=True)
    activity_code: str = Field(index=True)  # Stable code e.g., "S1_SC_NG"
    activity_name: str
    gas: str = Field(index=True)  # CO2, CH4, N2O, SF6, etc.
    factor_value: float
    factor_unit: str  # e.g., "kg CO2/GJ", "kg CH4/GJ"
    basis: str = Field(default="NA")  # HHV, LHV, NA
    oxidation_frac: Optional[float] = Field(default=1.0)
    fuel_state: str = Field(default="NA")  # gas, liquid, solid, NA
    source_authority: str = Field(index=True)  # DEFRA, EPA, IPCC, API, IEA
    source_doc: str
    source_table: Optional[str] = None
    source_year: int = Field(index=True)
    geography: str = Field(default="Global")
    region_code: Optional[str] = Field(default=None, index=True)  # ISO codes e.g., "EG", "US"
    market_or_location: str = Field(default="NA")  # location, market, NA
    technology: Optional[str] = None
    uncertainty_pct: Optional[float] = None
    valid_from: date
    valid_to: Optional[date] = None
    citation: Optional[str] = None
    method_equation_ref: Optional[str] = None  # e.g., "EPA C-1", "IPCC Vol2 Ch2 Eq 2.8"
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_ef_lookup', 'scope', 'subcategory', 'activity_code', 'gas', 'source_year'),
    )


class GWP(SQLModel, table=True):
    """Global Warming Potential values for different IPCC assessment reports."""
    __tablename__ = "gwp"

    id: Optional[int] = Field(default=None, primary_key=True)
    set_name: str = Field(index=True)  # AR5, AR6
    gas: str = Field(index=True)  # CO2, CH4, N2O, SF6, etc.
    horizon_yr: int = Field(default=100)  # 20, 100, 500
    value: float  # GWP value relative to CO2

    __table_args__ = (
        UniqueConstraint('set_name', 'gas', 'horizon_yr', name='uq_gwp'),
    )


class Calculation(SQLModel, table=True):
    """Immutable calculation records with full provenance."""
    __tablename__ = "calculations"

    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="activities.id", index=True)
    method_key: str
    input_snapshot_json: Dict[str, Any] = Field(sa_column=Column(JSON))  # Activity data at calc time
    factor_snapshot_json: Dict[str, Any] = Field(sa_column=Column(JSON))  # EF frozen snapshot
    results_json: Dict[str, Any] = Field(sa_column=Column(JSON))  # Output: CO2, CH4, N2O, CO2e
    calc_version: str = Field(default="1.0")
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    performed_by: Optional[str] = None  # Username or system

    # Relationships
    activity: Activity = Relationship(back_populates="calculations")


class Attachment(SQLModel, table=True):
    """Evidence files attached to activities."""
    __tablename__ = "attachments"

    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="activities.id", index=True)
    file_path: str  # Relative path under uploads/
    description: Optional[str] = None
    tag: Optional[str] = None  # e.g., "invoice", "meter_reading", "lab_report"
    file_hash: Optional[str] = None  # SHA256 for verification
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    activity: Activity = Relationship(back_populates="attachments")


class ReportSection(SQLModel, table=True):
    """User-editable text for ISO 14064-1 report sections."""
    __tablename__ = "report_sections"

    id: Optional[int] = Field(default=None, primary_key=True)
    org_id: int = Field(foreign_key="organizations.id", index=True)
    clause_key: str  # e.g., "intro", "boundaries", "methods"
    markdown_text: str
    version: int = Field(default=1)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    organization: Organization = Relationship(back_populates="report_sections")

    __table_args__ = (
        UniqueConstraint('org_id', 'clause_key', name='uq_org_clause'),
    )


class AuditTrail(SQLModel, table=True):
    """Audit log for all entity changes."""
    __tablename__ = "audit_trail"

    id: Optional[int] = Field(default=None, primary_key=True)
    entity_type: str = Field(index=True)  # "Activity", "EmissionFactor", etc.
    entity_id: int
    action: str  # "CREATE", "UPDATE", "DELETE"
    old_value_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    new_value_json: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    user: Optional[str] = None
    ts: datetime = Field(default_factory=datetime.utcnow, index=True)
