from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import create_tables, get_session
from app.models import PayloadRequest, PayloadResponse
from app.service import create_payload


@asynccontextmanager
async def lifespan(app: FastAPI):
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
