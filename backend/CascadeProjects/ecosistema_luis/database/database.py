from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .models import Base
import os

# Configuración de la base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite"
)

# Para desarrollo local con SQLite
if DATABASE_URL == "sqlite":
    DATABASE_URL = "sqlite:///./ecosistema_luis.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Crear todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configuración para Supabase
def get_supabase_client():
    """Obtener cliente de Supabase"""
    try:
        from supabase import create_client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if supabase_url and supabase_key:
            return create_client(supabase_url, supabase_key)
    except ImportError:
        pass
    return None
