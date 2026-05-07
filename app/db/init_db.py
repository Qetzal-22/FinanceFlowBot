from dotenv import load_dotenv
import os
import logging

from app.db.database import Base, engine
from app.db import models
from app.db import crud

load_dotenv()
logger = logging.getLogger(__name__)

async def init_models():
    async with engine.begin() as conn:
        if os.getenv("AUTO_CREATE_TABLES") != "1":
            return
        await conn.run_sync(Base.metadata.create_all)
        logger.info("CREATED TABLES")
    categories = await crud.get_categories_all()
    has_transfer_category = False
    transfer_category = str(os.getenv("CATEGORY_FOR_TRANSFER"))
    for category in categories:
        if category.name == transfer_category:
            has_transfer_category = True
    if not has_transfer_category:
        await crud.create_category(transfer_category)
