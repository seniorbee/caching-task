from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import create_tables, get_session
from app.models import PayloadRequest, PayloadResponse, PayloadOutput
from app.service import create_payload
from app.dao import PayloadCacheDAO


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize persistent storage before accepting requests.

    Tables are created at application startup rather than per request so
    database initialization is performed once during the application
    lifecycle.
    """
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/payload", response_model=PayloadResponse)
async def create_payload_endpoint(
    payload: PayloadRequest,
    session: AsyncSession = Depends(get_session),
) -> PayloadResponse:
    payload_id = await create_payload(
        session,
        payload.list_1,
        payload.list_2,
    )

    return PayloadResponse(id=payload_id)


@app.get("/payload/{id}", response_model=PayloadOutput)
async def get_payload(
    id: str,
    session: AsyncSession = Depends(get_session),
) -> PayloadOutput:
    dao = PayloadCacheDAO(session)
    payload = await dao.get(id)

    if payload is None:
        raise HTTPException(status_code=404, detail="Payload not found")

    return PayloadOutput(output=payload.output)
