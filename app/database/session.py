# app/database/session.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings

async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False
)


async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session