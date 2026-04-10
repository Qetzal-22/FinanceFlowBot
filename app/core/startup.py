from app.scheduler.scheduler import start_scheduler
from app.scheduler.jobs import update_budget

async def startup():
    await update_budget()
    await start_scheduler()
