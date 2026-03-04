"""Aggregate API routers."""

from fastapi import APIRouter

from app.api import alertdefs, auth, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(alertdefs.router)
