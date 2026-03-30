import asyncio
import logging

from app.db.init_db import init_models
from app.config.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)



async def main():
    for i in range(1, 11):
        try:
            logger.info("initial db try connection count_try=%s", i)
            await init_models()
            logger.info("initial db successful connection")
            return
        except Exception as e:
            logger.info("initial db error connection error=%s", e)
            await asyncio.sleep(2)
    raise Exception("Error connection to DB")


if __name__ == "__main__":
    asyncio.run(main())