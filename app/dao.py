from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.tables import PayloadCache, TransformationCache


class TransformationCacheDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, input: str) -> TransformationCache | None:
        result = await self.session.execute(
            select(TransformationCache).where(
                TransformationCache.input == input
            )
        )
        return result.scalar_one_or_none()

    async def save(self, input: str, output: str) -> None:
        self.session.add(
            TransformationCache(input=input, output=output)
        )


class PayloadCacheDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, hash: str) -> PayloadCache | None:
        result = await self.session.execute(
            select(PayloadCache).where(
                PayloadCache.hash == hash
            )
        )
        return result.scalar_one_or_none()

    async def save(self, hash: str, output: str) -> None:
        self.session.add(
            PayloadCache(hash=hash, output=output)
        )