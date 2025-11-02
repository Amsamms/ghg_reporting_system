"""
Database session management and initialization.
"""

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from pathlib import Path
from typing import Generator


# Database path
DB_PATH = Path(__file__).parent.parent / "ghg_inventory.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine with proper settings
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def create_db_and_tables():
    """Initialize database and create all tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session (dependency injection for FastAPI/etc)."""
    with Session(engine) as session:
        yield session


def get_db() -> Session:
    """Get database session (direct use)."""
    return Session(engine)


def init_db():
    """Initialize database with required seed data."""
    create_db_and_tables()

    # Import models to ensure they're registered
    from . import models

    # Seed GWP values if not present
    with Session(engine) as session:
        from .models import GWP

        # Check if GWP data exists
        existing = session.query(GWP).first()
        if not existing:
            # AR5 100-year GWP values (IPCC Fifth Assessment Report)
            gwp_ar5 = [
                GWP(set_name="AR5", gas="CO2", horizon_yr=100, value=1),
                GWP(set_name="AR5", gas="CH4", horizon_yr=100, value=28),
                GWP(set_name="AR5", gas="N2O", horizon_yr=100, value=265),
                GWP(set_name="AR5", gas="SF6", horizon_yr=100, value=23500),
                GWP(set_name="AR5", gas="HFC-134a", horizon_yr=100, value=1300),
                GWP(set_name="AR5", gas="HFC-32", horizon_yr=100, value=677),
                GWP(set_name="AR5", gas="HFC-125", horizon_yr=100, value=3170),
                GWP(set_name="AR5", gas="CF4", horizon_yr=100, value=6630),
            ]

            # AR6 100-year GWP values (IPCC Sixth Assessment Report)
            gwp_ar6 = [
                GWP(set_name="AR6", gas="CO2", horizon_yr=100, value=1),
                GWP(set_name="AR6", gas="CH4", horizon_yr=100, value=27.9),
                GWP(set_name="AR6", gas="N2O", horizon_yr=100, value=273),
                GWP(set_name="AR6", gas="SF6", horizon_yr=100, value=25200),
                GWP(set_name="AR6", gas="HFC-134a", horizon_yr=100, value=1530),
                GWP(set_name="AR6", gas="HFC-32", horizon_yr=100, value=771),
                GWP(set_name="AR6", gas="HFC-125", horizon_yr=100, value=3740),
                GWP(set_name="AR6", gas="CF4", horizon_yr=100, value=7380),
            ]

            for gwp in gwp_ar5 + gwp_ar6:
                session.add(gwp)

            session.commit()
            print("✓ GWP values seeded successfully")

        # Seed common emission sources
        from .models import Source
        existing_sources = session.query(Source).first()
        if not existing_sources:
            sources = [
                # Scope 1 sources
                Source(scope=1, subcategory="stationary_combustion", description="Stationary fuel combustion"),
                Source(scope=1, subcategory="mobile_combustion", description="Mobile fuel combustion"),
                Source(scope=1, subcategory="flaring", description="Flare and thermal oxidizer"),
                Source(scope=1, subcategory="fugitives", description="Fugitive equipment leaks"),
                Source(scope=1, subcategory="process_co2", description="Process CO2 emissions"),
                Source(scope=1, subcategory="venting", description="Intentional venting"),

                # Scope 2 sources
                Source(scope=2, subcategory="purchased_electricity", description="Purchased electricity"),
                Source(scope=2, subcategory="purchased_steam", description="Purchased steam"),
                Source(scope=2, subcategory="purchased_heat", description="Purchased heating"),
                Source(scope=2, subcategory="purchased_cooling", description="Purchased cooling"),

                # Scope 3 sources (key categories for petroleum)
                Source(scope=3, subcategory="transport_upstream", description="Upstream transportation"),
                Source(scope=3, subcategory="transport_downstream", description="Downstream transportation"),
                Source(scope=3, subcategory="business_travel", description="Business travel"),
                Source(scope=3, subcategory="employee_commuting", description="Employee commuting"),
                Source(scope=3, subcategory="waste_disposal", description="Waste disposal"),
            ]

            for source in sources:
                session.add(source)

            session.commit()
            print("✓ Emission sources seeded successfully")
