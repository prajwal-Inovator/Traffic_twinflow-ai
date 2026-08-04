# negotiation_engine/junction_agent.py
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .negotiation_protocol import JunctionState, MasterRecommendation, NegotiationMessage
from .message_broker import broker

logger = logging.getLogger(__name__)

class JunctionAgent:
    """
    AI Agent representing a single traffic junction.
    It collects state, exchanges with neighbors, and receives recommendations.
    """

    def __init__(
        self,
        junction_id: str,
        neighbors: List[str] = None,
        state: Optional[JunctionState] = None,
    ):
        self.junction_id = junction_id
        self.neighbors = neighbors or []
        self.state = state or JunctionState(
            junction_id=junction_id,
            vehicle_count=0,
            queue_length=0,
            signal_phase="green",
            predicted_vehicles=0,
            emergency_status=False,
            bus_priority=False,
            pollution=0.0,
            weather="clear",
            current_delay=0.0,
        )
        self.last_recommendation: Optional[MasterRecommendation] = None
        self.is_running = False
        self._task = None

        # Subscribe to topics
        self._subscriptions = []

    async def start(self):
        """Start the agent: subscribe to relevant topics."""
        self.is_running = True
        # Subscribe to recommendations for this junction
        topic_rec = f"recommendation:{self.junction_id}"
        await broker.subscribe(topic_rec, self._handle_recommendation)
        self._subscriptions.append(topic_rec)

        # Subscribe to state updates from neighbors (optional)
        for neighbor in self.neighbors:
            topic_state = f"state:{neighbor}"
            await broker.subscribe(topic_state, self._handle_neighbor_state)
            self._subscriptions.append(topic_state)

        # Periodic broadcast of state
        self._task = asyncio.create_task(self._broadcast_loop())
        logger.info(f"JunctionAgent {self.junction_id} started.")

    async def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
        # Unsubscribe
        for topic in self._subscriptions:
            # We need a way to remove the callback; for simplicity, we just clear.
            pass
        logger.info(f"JunctionAgent {self.junction_id} stopped.")

    async def update_state(self, new_state: Dict[str, Any]):
        """Update the agent's local state."""
        for key, value in new_state.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
        self.state.timestamp = datetime.utcnow()
        # Optionally broadcast immediately
        await self.publish_state()

    async def publish_state(self):
        """Publish the current state to the broker."""
        message = NegotiationMessage(
            type="state_update",
            sender_id=self.junction_id,
            recipient_id=None,  # broadcast
            payload=self.state.dict(),
        )
        await broker.publish(f"state:{self.junction_id}", message)
        # Also publish to master agent (if needed)
        await broker.publish("master:state", message)

    async def _broadcast_loop(self, interval: int = 5):
        """Periodically broadcast state."""
        while self.is_running:
            try:
                await self.publish_state()
            except Exception as e:
                logger.error(f"Error in broadcast loop for {self.junction_id}: {e}")
            await asyncio.sleep(interval)

    async def _handle_recommendation(self, message: NegotiationMessage):
        """Handle a recommendation from the master agent."""
        if message.payload:
            rec = MasterRecommendation(**message.payload)
            self.last_recommendation = rec
            logger.info(f"Junction {self.junction_id} received recommendation: {rec.reason}")
            # Apply recommendation (e.g., change signal timing)
            # This would be done via backend/SUMO integration
            await self.apply_recommendation(rec)

    async def _handle_neighbor_state(self, message: NegotiationMessage):
        """Handle state updates from neighbors."""
        # We can store neighbor states for local decision-making if needed
        pass

    async def apply_recommendation(self, rec: MasterRecommendation):
        """Apply the recommendation to the traffic signal."""
        # In production, this would call the backend or SUMO to update signal timings
        # For now, we log and update local state
        logger.info(f"Applying recommendation for {self.junction_id}: green={rec.green_time}s, red={rec.red_time}s")
        # Update local state phase? We'll keep it abstract.
        self.state.signal_phase = "green" if rec.green_time > 0 else "red"  # simplified