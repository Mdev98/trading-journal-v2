"""
Configuration de la base de données SQLAlchemy
Support SQLite (dev) et PostgreSQL (prod)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de la base de données (SQLite par défaut, PostgreSQL en prod)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./trading_journal.db"
)

# Fix pour PostgreSQL sur Render (postgres:// -> postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configuration du moteur SQLAlchemy
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def get_db():
    """
    Générateur de session de base de données.
    À utiliser comme dépendance FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
