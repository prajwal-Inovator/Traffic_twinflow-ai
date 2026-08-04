# backend/app/websocket/handlers.py
import socketio
from typing import Dict, Any
import logging
from ..websocket.manager import manager
from ..core.security import decode_token
from ..core.database import get_db
from ..services.traffic_service import TrafficService
from ..services.negotiation_service import NegotiationService
from ..services.simulation_service import SimulationService

logger = logging.getLogger(__name__)

# Define Socket.IO namespace (can be /ws or /)
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode="asgi",
    logger=False,
    engineio_logger=False,
)

@sio.event
async def connect(sid: str, environ: Dict, auth: Dict = None):
    """Handle new connection with optional JWT authentication."""
    user_id = None
    roles = []

    # Try to authenticate via auth dict or query string
    token = auth.get("token") if auth else None
    if not token:
        # Fallback: check query string
        query_string = environ.get("QUERY_STRING", "")
        params = dict(qc.split("=") for qc in query_string.split("&") if "=" in qc)
        token = params.get("token")

    if token:
        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            user_id = payload.get("sub")
            roles = [payload.get("role", "driver")]
            logger.info(f"Authenticated WebSocket for user {user_id}")

    await manager.connect(sid, user_id, roles)

    # Join rooms based on role
    if "admin" in roles or "authority" in roles:
        await manager.join_room(sid, "authority")
    if "driver" in roles:
        await manager.join_room(sid, "drivers")
    if "emergency" in roles:
        await manager.join_room(sid, "emergency")

    # Send welcome message
    await sio.emit("connected", {"status": "ok", "user_id": user_id}, room=sid)

@sio.event
async def disconnect(sid: str):
    await manager.disconnect(sid)

@sio.event
async def subscribe(sid: str, data: Dict):
    """Subscribe to specific junction updates."""
    junction_id = data.get("junction_id")
    if junction_id:
        room = f"junction_{junction_id}"
        await manager.join_room(sid, room)
        await sio.emit("subscribed", {"junction_id": junction_id}, room=sid)
    else:
        # Subscribe to all updates
        await manager.join_room(sid, "all_traffic")
        await sio.emit("subscribed", {"scope": "all"}, room=sid)

@sio.event
async def unsubscribe(sid: str, data: Dict):
    junction_id = data.get("junction_id")
    if junction_id:
        room = f"junction_{junction_id}"
        await manager.leave_room(sid, room)
    else:
        await manager.leave_room(sid, "all_traffic")

@sio.event
async def trigger_negotiation(sid: str, data: Dict):
    """Client requests a negotiation for a junction."""
    junction_id = data.get("junction_id")
    if not junction_id:
        await sio.emit("error", {"message": "Missing junction_id"}, room=sid)
        return

    # Use a database session (we need to inject it)
    db = get_db()
    service = NegotiationService(db)
    result = await service.trigger_negotiation(junction_id)

    # Broadcast result to all authority users and to the specific junction room
    await sio.emit("negotiation_triggered", {
        "junction_id": junction_id,
        "negotiation_id": result.get("negotiation_id"),
        "status": "processing",
    }, room=sid)

    # In a real system, the negotiation would be async and we'd broadcast when done.
    # For now, we simulate by calling the service and pushing a recommendation later.

@sio.event
async def run_simulation(sid: str, data: Dict):
    """Client requests a simulation run."""
    params = data.get("params", {})
    db = get_db()
    service = SimulationService(db)
    sim_id = await service.run_simulation(params)

    await sio.emit("simulation_started", {
        "simulation_id": sim_id,
        "status": "running",
    }, room=sid)

    # In production, we'd run the simulation asynchronously and emit results.