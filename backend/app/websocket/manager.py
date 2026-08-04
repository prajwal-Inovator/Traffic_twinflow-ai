# backend/app/websocket/manager.py
import asyncio
from typing import Dict, Set, Optional, Any
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manage WebSocket connections with room support."""

    def __init__(self):
        # active_connections: sid -> dict with user info, rooms, etc.
        self.active_connections: Dict[str, Dict] = {}
        # rooms: room_name -> set of sids
        self.rooms: Dict[str, Set[str]] = {}

    async def connect(self, sid: str, user_id: Optional[str] = None, roles: list = None):
        """Register a new connection."""
        self.active_connections[sid] = {
            "user_id": user_id,
            "roles": roles or [],
            "joined_at": datetime.utcnow().isoformat() + "Z",
        }
        logger.info(f"WebSocket connected: {sid} (user: {user_id})")

    async def disconnect(self, sid: str):
        """Remove a connection and leave all rooms."""
        if sid in self.active_connections:
            del self.active_connections[sid]
        # Remove from all rooms
        for room in list(self.rooms.keys()):
            if sid in self.rooms[room]:
                self.rooms[room].remove(sid)
                if not self.rooms[room]:
                    del self.rooms[room]
        logger.info(f"WebSocket disconnected: {sid}")

    async def join_room(self, sid: str, room: str):
        """Add a sid to a room."""
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(sid)
        logger.debug(f"SID {sid} joined room {room}")

    async def leave_room(self, sid: str, room: str):
        """Remove a sid from a room."""
        if room in self.rooms and sid in self.rooms[room]:
            self.rooms[room].remove(sid)
            if not self.rooms[room]:
                del self.rooms[room]
            logger.debug(f"SID {sid} left room {room}")

    async def get_connections_in_room(self, room: str) -> list:
        """Get list of sids in a room."""
        return list(self.rooms.get(room, set()))

    async def broadcast_to_room(self, room: str, event: str, data: Any, sio):
        """Emit an event to all clients in a room."""
        if room in self.rooms:
            for sid in self.rooms[room]:
                await sio.emit(event, data, room=sid, skip_sid=None)

    async def broadcast_to_all(self, event: str, data: Any, sio):
        """Emit an event to all connected clients."""
        for sid in self.active_connections.keys():
            await sio.emit(event, data, room=sid, skip_sid=None)

manager = ConnectionManager()