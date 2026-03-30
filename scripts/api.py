import logging
import os
from dotenv import load_dotenv
import asyncio

from fastapi import FastAPI
from uvicorn import Config, Server
from starlette.middleware.sessions import SessionMiddleware

from app.api.routers.admin import admin_router
from app.config.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI()

app.include_router(admin_router)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY")
)

async def start_api():
    config = Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = Server(config)
    logger.info("Admin panel: http://localhost:8000/admin/dashboard")
    return await server.serve()

if __name__ == "__main__":
    asyncio.run(start_api())