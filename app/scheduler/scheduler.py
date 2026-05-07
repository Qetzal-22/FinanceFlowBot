import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.scheduler.jobs import update_budget

scheduler = AsyncIOScheduler(timezone="Asia/Vladivostok")

async def start_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        update_budget,
        "cron",
        day=1,
        hour=0,
        minute=0,
    )

    scheduler.start()

async def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)

if __name__ == "__main__":
    asyncio.run(start_scheduler())