from app.scheduler.scheduler import stop_scheduler

async def shutdown():
    await stop_scheduler()