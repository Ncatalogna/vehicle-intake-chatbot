import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker

load_dotenv()

# Construir la URL de la base de datos a partir de las variables de entorno
DB_HOST = os.getenv("DB_POSTGRES_HOST")
DB_PORT = os.getenv("DB_POSTGRES_PORT")
DB_USER = os.getenv("DB_POSTGRES_USER")
DB_PASSWORD = os.getenv("DB_POSTGRES_PASSWORD")
DB_NAME = os.getenv("DB_POSTGRES_DB")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async_engine = create_async_engine(DATABASE_URL, echo=True)

# Se usa async_sessionmaker para sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Dependency to get a DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- Alembic support ---
def get_database_url() -> str:
    """Returns the synchronous database URL for Alembic."""
    return DATABASE_URL.replace("+asyncpg", "")

def get_engine():
    """Returns a synchronous engine for Alembic."""
    return create_engine(get_database_url())