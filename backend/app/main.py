import logging
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.integration import get_simulation_data, get_ai_prediction
from app.core.database import connect_to_mongo
from .api.router import api_router
from .core.config import settings
from .core.exceptions import setup_exception_handlers
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
async def lifespan(app: FastAPI):
    try:
        await connect_to_mongo()
        logging.info("✅ MongoDB connected")
    except Exception as e:
        logging.error(f"❌ MongoDB failed: {e}")

    yield

# --------------------------------------------------
# FastAPI
# --------------------------------------------------

fastapi_app = FastAPI(
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

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Exception Handlers
# --------------------------------------------------

setup_exception_handlers(fastapi_app)

# --------------------------------------------------
# Routes
# --------------------------------------------------

fastapi_app.include_router(api_router, prefix="/api")

# --------------------------------------------------
# Health
# --------------------------------------------------

@fastapi_app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "twinflow-backend",
    }

# --------------------------------------------------
# Socket.IO (IMPORTANT FIX)
# --------------------------------------------------

# Wrap FastAPI inside Socket.IO
app = socketio.ASGIApp(
    sio,
    other_asgi_app=fastapi_app,
)

@app.get("/smart-traffic")
def smart_traffic():
    sim_data = get_simulation_data()

    if "error" in sim_data:
        return sim_data

    ai_result = get_ai_prediction(sim_data)

    return {
        "simulation": sim_data,
        "ai_analysis": ai_result
    }

@app.get("/live-monitor")
def live_monitor():
    data = []

    for _ in range(5):
        sim = get_simulation_data()
        ai = get_ai_prediction(sim)

        data.append({
            "simulation": sim,
            "ai": ai
        })

    return data