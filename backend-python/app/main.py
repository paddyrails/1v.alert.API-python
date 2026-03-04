"""FastAPI app: config, logging, CORS, routers, middleware."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.exception_handler import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure settings and logging are loaded
    settings = get_settings()
    configure_logging(settings.log_level)
    yield
    # Shutdown: nothing to do for now
    pass


app = FastAPI(
    title=get_settings().app_name,
    lifespan=lifespan,
)

# Middleware: correlation ID first (so it's set for exception handlers)
app.add_middleware(CorrelationIdMiddleware)
register_exception_handlers(app)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router)
