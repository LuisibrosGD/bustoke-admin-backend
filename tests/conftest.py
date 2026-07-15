import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.database import AsyncSessionLocal, engine, get_db
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def setup_db():
    from app.core.security import get_password_hash
    from app.database import Base

    async with engine.begin() as conn:
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


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(setup_db) -> AsyncGenerator:
    transport = ASGITransport(app=app)

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
