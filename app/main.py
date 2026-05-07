import logging
import os
from dotenv import load_dotenv
import asyncio

from contextlib import asynccontextmanager
from fastapi import FastAPI
from uvicorn import Config, Server
from starlette.middleware.sessions import SessionMiddleware

from app.api.routers.admin import admin_router
from app.config.logging_config import setup_logging
from app.core.startup import startup
from app.core.shutdown import shutdown

setup_logging()

logger = logging.getLogger(__name__)
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()


app = FastAPI(title="Finance Flow", lifespan=lifespan)

app.include_router(admin_router)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY")
)