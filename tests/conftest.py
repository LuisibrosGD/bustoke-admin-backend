from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings


@pytest.fixture(autouse=True)
def _reset_rate_limit():
    """Limpia el estado en memoria del rate limiter antes de cada test para que
    los múltiples logins de la suite (mismo email) no disparen el 429."""
    from app.core.rate_limit import _hits

    _hits.clear()
    yield


@pytest_asyncio.fixture(scope="session")
async def setup_db():
    from app.core.security import get_password_hash
    from app.database import Base

    test_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

            tipo_exists = await conn.execute(
                text("SELECT 1 FROM tipos_documento LIMIT 1")
            )
            if not tipo_exists.scalar():
                await conn.execute(
                    text("INSERT INTO tipos_documento (nombre, abreviatura) VALUES ('DNI', 'DNI')")
                )

            hashed = get_password_hash("TempPassword123!5")
            await conn.execute(
                text("UPDATE usuarios SET password_hash = :hash WHERE id_usuario = 5"),
                {"hash": hashed},
            )
    finally:
        await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(setup_db) -> AsyncGenerator:
    from app.database import get_db
    from app.main import app

    test_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    transport = ASGITransport(app=app)

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await test_engine.dispose()
