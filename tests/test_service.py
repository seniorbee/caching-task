import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.dao import TransformationCacheDAO
from app.service import create_payload
from app.tables import Base


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_payload(session):
    payload_id = await create_payload(
        session,
        ["hello", "world"],
        ["foo", "bar"],
    )

    assert len(payload_id) == 64


@pytest.mark.asyncio
async def test_same_payload_returns_same_id(session):
    first_id = await create_payload(
        session,
        ["hello", "world"],
        ["foo", "bar"],
    )

    second_id = await create_payload(
        session,
        ["hello", "world"],
        ["foo", "bar"],
    )

    assert first_id == second_id


@pytest.mark.asyncio
async def test_different_payload_returns_different_id(session):
    first_id = await create_payload(
        session,
        ["hello", "world"],
        ["foo", "bar"],
    )

    second_id = await create_payload(
        session,
        ["hello", "python"],
        ["foo", "bar"],
    )

    assert first_id != second_id


@pytest.mark.asyncio
async def test_transformation_cache_is_reused(session):
    await create_payload(
        session,
        ["hello", "world"],
        ["foo", "bar"],
    )

    dao = TransformationCacheDAO(session)

    hello = await dao.get("hello")
    world = await dao.get("world")
    foo = await dao.get("foo")
    bar = await dao.get("bar")

    assert hello.output == "HELLO"
    assert world.output == "WORLD"
    assert foo.output == "FOO"
    assert bar.output == "BAR"


@pytest.mark.asyncio
async def test_existing_payload_does_not_create_transformations(session):
    await create_payload(
        session,
        ["hello", "world"],
        ["foo", "bar"],
    )

    first_id = await create_payload(
        session,
        ["hello", "world"],
        ["foo", "bar"],
    )

    second_id = await create_payload(
        session,
        ["hello", "world"],
        ["foo", "bar"],
    )

    assert first_id == second_id