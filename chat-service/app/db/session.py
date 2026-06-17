from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from app.core.config import settings
from app.db.base import Base
from app.models.user import User
from app.models.file import File

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool if settings.DEBUG and "sqlite" in settings.DATABASE_URL else None,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with engine.connect() as conn:
        await conn.execute(text("CREATE TABLE IF NOT EXISTS users (id VARCHAR PRIMARY KEY, email VARCHAR UNIQUE, hashed_password VARCHAR)"))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id VARCHAR NOT NULL UNIQUE,
                filename VARCHAR NOT NULL,
                project_id VARCHAR,
                status VARCHAR(10) NOT NULL DEFAULT 'pending',
                context_id VARCHAR,
                sha256 VARCHAR,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
            )
        """))
        await conn.commit()
    
    print("✅ База данных инициализирована")

async def shutdown_db():
    await engine.dispose()