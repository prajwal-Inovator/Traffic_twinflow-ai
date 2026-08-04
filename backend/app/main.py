# backend/app/main.py (updated)
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from .api.router import api_router
from .core.config import settings
from .core.logging import setup_logging
from .core.exceptions import setup_exception_handlers
from .core.database import connect_to_mongo, close_mongo_connection
from .websocket.handlers import sio
from .core.redis import close_redis
from .core.indexes import ensure_indexes

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TwinFlow AI Backend")
    await connect_to_mongo()
    await ensure_indexes()   # <-- add this
    yield
    await close_mongo_connection()
    logger.info("Shutting down TwinFlow AI Backend")


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TwinFlow AI Backend")
    await connect_to_mongo()
    yield
    await close_mongo_connection()
    logger.info("Shutting down TwinFlow AI Backend")

# Create FastAPI app
app = FastAPI(
    title="TwinFlow AI API",
    description="Smart City Digital Twin - Traffic Management & AI Negotiation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
setup_exception_handlers(app)

# Include API router
app.include_router(api_router, prefix="/api")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "twinflow-backend"}

# ---- Mount Socket.IO ----
# Create an ASGI application that combines FastAPI and Socket.IO
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware as StarletteCORSMiddleware
from starlette.routing import Mount, Route

# We will use socketio.ASGIApp with FastAPI as WSGI/ASGI mount
# The easiest is to create a combined ASGI app:
from socketio import ASGIApp

# Create the ASGI app that routes requests to either FastAPI or Socket.IO
socketio_app = ASGIApp(sio, other_asgi_app=app)

# Replace the original app with the combined one
# In uvicorn we can run socketio_app directly.
# We'll export socketio_app as the main application.

# For convenience, we keep a reference to the original fastapi app for uvicorn
# But we'll actually use the combined app.
# We can set the main entry point to the combined app.
# Since uvicorn expects a callable, we can just assign app = socketio_app.
# But we also need to keep the original app for other purposes.

# We'll do:
original_app = app
app = socketio_app  # now the ASGI app is the combined one

# Also ensure we can still access FastAPI app via original_app for docs/health (but not needed)