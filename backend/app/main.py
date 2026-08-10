# backend/app/main.py

import logging
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import connect_to_mongo
from .api.router import api_router
from .core.config import settings
from .core.exceptions import setup_exception_handlers
from .core.database import connect_to_mongo, close_mongo_connection
from .core.indexes import ensure_indexes
from .websocket.handlers import sio

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Lifespan
# --------------------------------------------------
@asynccontextmanager
async def lifespan(app):
    try:
        await connect_to_mongo()
        logging.info("MongoDB connected")
    except Exception as e:
        logging.error(f"MongoDB failed: {e}")

    yield
# --------------------------------------------------
# FastAPI
# --------------------------------------------------
app = FastAPI(
    title="TwinFlow AI API",
    description="Smart City Digital Twin - Traffic Management & AI Negotiation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# --------------------------------------------------
# CORS
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Exception Handlers
# --------------------------------------------------
setup_exception_handlers(app)

# --------------------------------------------------
# Routes
# --------------------------------------------------
app.include_router(api_router, prefix="/api")

# --------------------------------------------------
# Health
# --------------------------------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "twinflow-backend",
    }

# --------------------------------------------------
# Socket.IO
# --------------------------------------------------
socketio_app = socketio.ASGIApp(
    sio,
    other_asgi_app=app,
)

# Keep FastAPI reference
original_app = app

# Export Socket.IO app
app = socketio_app

@app.get("/health")
async def health():
    return {"status": "ok"}