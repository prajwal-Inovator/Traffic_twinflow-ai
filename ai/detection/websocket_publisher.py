# ai/detection/websocket_publisher.py
import asyncio
import socketio
from .main import DetectionEngine
import logging

logger = logging.getLogger(__name__)

class DetectionPublisher:
    """Publish detection results to a Socket.IO server."""

    def __init__(
        self,
        server_url: str = "http://localhost:8000",
        video_source: str = "0",
        model_path: str = "yolo11n.pt",
        device: str = "cpu",
    ):
        self.server_url = server_url
        self.video_source = video_source
        self.sio = socketio.AsyncClient()
        self.engine = DetectionEngine(model_path=model_path, device=device)
        self.is_connected = False

    async def connect(self):
        """Connect to Socket.IO server."""
        @self.sio.event
        async def connect():
            self.is_connected = True
            logger.info("Connected to Socket.IO server.")
            # Start detection once connected
            asyncio.create_task(self._run_detection())

        @self.sio.event
        async def disconnect():
            self.is_connected = False
            logger.info("Disconnected from Socket.IO server.")

        await self.sio.connect(self.server_url, transports=['websocket'])

    async def _run_detection(self):
        """Run detection and publish results."""
        async def on_detection(detections):
            if self.is_connected:
                await self.sio.emit("detection", {"detections": detections})
        async def on_track(tracked):
            if self.is_connected:
                await self.sio.emit("tracking", {"tracked": tracked})
        await self.engine.process_video(
            self.video_source,
            on_detection=on_detection,
            on_track=on_track,
        )

    async def start(self):
        await self.connect()
        # Keep running
        while True:
            await asyncio.sleep(1)

    async def stop(self):
        self.engine.stop()
        await self.sio.disconnect()