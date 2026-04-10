from app.services.budget import update_budget_new_month

async def update_budget():
    await update_budget_new_month()