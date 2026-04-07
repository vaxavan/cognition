from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings

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

async def init_db():
    from app.models.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных инициализирована")

async def shutdown_db():
    await engine.dispose()
