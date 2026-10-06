from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.tables import PayloadCache, TransformationCache


class TransformationCacheDAO:
    """Database access for individual transformation results.

    Kept separate from PayloadCacheDAO because transformation results have a
    different cache key and lifecycle: one transformed value can be reused by
    many different payloads.
    """
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
        """Stage a cache entry for persistence.
        The service layer controls the transaction so multiple cache writes and
        the final payload write are committed together."""
        self.session.add(
            TransformationCache(input=input, output=output)
        )


class PayloadCacheDAO:
    """Database access for complete generated payloads.

    The deterministic payload hash is used directly as the primary key, which
    makes an exact duplicate request naturally resolve to the existing entry.
    """
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
        """Stage a cache entry for persistence.
        The service layer controls the transaction so multiple cache writes and
        the final payload write are committed together."""
        self.session.add(
            PayloadCache(hash=hash, output=output)
        )