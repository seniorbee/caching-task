import hashlib
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.dao import PayloadCacheDAO, TransformationCacheDAO
from app.transformer import transform


def get_payload_hash(list_1: list[str], list_2: list[str]) -> str:
    data = json.dumps(
        [list_1, list_2],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(data.encode()).hexdigest()


async def get_or_create_transformation(
    value: str,
    dao: TransformationCacheDAO,
) -> str:
    cached = await dao.get(value)

    if cached is not None:
        return cached.output

    output = transform(value)
    await dao.save(value, output)

    return output


async def create_payload(
    session: AsyncSession,
    list_1: list[str],
    list_2: list[str],
) -> str:
    payload_dao = PayloadCacheDAO(session)

    payload_hash = get_payload_hash(list_1, list_2)

    cached_payload = await payload_dao.get(payload_hash)

    if cached_payload is not None:
        return cached_payload.hash

    transformation_dao = TransformationCacheDAO(session)

    transformed_1 = []
    transformed_2 = []

    for value in list_1:
        transformed_1.append(
            await get_or_create_transformation(
                value,
                transformation_dao,
            )
        )

    for value in list_2:
        transformed_2.append(
            await get_or_create_transformation(
                value,
                transformation_dao,
            )
        )

    output = ", ".join(
        value
        for pair in zip(transformed_1, transformed_2)
        for value in pair
    )

    await payload_dao.save(payload_hash, output)
    await session.commit()

    return payload_hash