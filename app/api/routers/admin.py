from fastapi import APIRouter, Request
from app.templates.templates import templates

admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})