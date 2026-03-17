from dotenv import load_dotenv
import os

from app.db.database import Base, engine

load_dotenv()

async def init_models():
    async with engine.begin() as conn:
        if os.getenv("AUTO_CREATE_TABLES") != "1":
            return
        await conn.run_sync(Base.metadata.create_all)