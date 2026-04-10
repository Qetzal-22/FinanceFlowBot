import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.scheduler.jobs import update_budget

async def start_scheduler():
    scheduler = AsyncIOScheduler(timezone="Asia/Vladivostok")
    scheduler.add_job(
        update_budget,
        "cron",
        day=1,
        hour=0,
        minute=0,
    )

    scheduler.start()

if __name__ == "__main__":
    asyncio.run(start_scheduler())