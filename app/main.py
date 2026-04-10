import logging
import os
from dotenv import load_dotenv
import asyncio

from fastapi import FastAPI
from uvicorn import Config, Server
from starlette.middleware.sessions import SessionMiddleware

from app.api.routers.admin import admin_router
from app.config.logging_config import setup_logging
from app.core.startup import startup

setup_logging()

logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI()

app.include_router(admin_router)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY")
)

@app.on_event("startup")
async def on_startup():
    await startup()
