# negotiation_engine/master_agent.py
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from .negotiation_protocol import JunctionState, MasterRecommendation, NegotiationMessage
from .message_broker import broker

logger = logging.getLogger(__name__)

class MasterAgent:
    """
    Master Negotiation Agent – aggregates states from all junctions,
    computes optimal signal timings, and broadcasts recommendations.
    """

    def __init__(self):
        self.junction_states: Dict[str, JunctionState] = {}
        self.last_recommendations: Dict[str, MasterRecommendation] = {}
        self.is_running = False
        self._task = None

    async def start(self):
        """Start listening to junction state updates."""
        self.is_running = True
        await broker.subscribe("master:state", self._handle_state_update)
        # Also listen for direct requests? Not needed.
        self._task = asyncio.create_task(self._decision_loop())
        logger.info("MasterAgent started.")

    async def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
        logger.info("MasterAgent stopped.")

    async def _handle_state_update(self, message: NegotiationMessage):
        """Receive state update from a junction."""
        if message.payload:
            state = JunctionState(**message.payload)
            self.junction_states[state.junction_id] = state
            logger.debug(f"MasterAgent received state from {state.junction_id}")

    async def _decision_loop(self, interval: int = 3):
        """Periodically compute recommendations for all junctions."""
        while self.is_running:
            try:
                if self.junction_states:
                    await self.compute_recommendations()
            except Exception as e:
                logger.error(f"Error in decision loop: {e}")
            await asyncio.sleep(interval)

    async def compute_recommendations(self, junction_id: Optional[str] = None):
        """Compute recommendations for all junctions or a specific one."""
        targets = [junction_id] if junction_id else list(self.junction_states.keys())

        for jid in targets:
            if jid not in self.junction_states:
                continue
            state = self.junction_states[jid]
            # Gather neighbor states (if we have them)
            neighbors = await self._get_neighbor_states(jid)

            # Compute recommendation
            rec = self._compute_single_recommendation(state, neighbors)
            self.last_recommendations[jid] = rec

            # Publish recommendation
            message = NegotiationMessage(
                type="recommendation",
                sender_id="master",
                recipient_id=jid,
                payload=rec.dict(),
            )
            await broker.publish(f"recommendation:{jid}", message)
            logger.info(f"MasterAgent published recommendation for {jid}: {rec.reason}")

    async def _get_neighbor_states(self, junction_id: str) -> List[JunctionState]:
        """Retrieve states of neighbors (if we have them)."""
        # In a real system, we would have a topology graph.
        # For now, we'll simulate by returning all states.
        return [s for jid, s in self.junction_states.items() if jid != junction_id]

    def _compute_single_recommendation(
        self,
        state: JunctionState,
        neighbors: List[JunctionState]
    ) -> MasterRecommendation:
        """
        Compute optimal green/red times for a single junction.
        Uses a rule-based algorithm with explainability.
        """
        # Basic factors:
        # - More vehicles -> need more green time
        # - Longer queue -> need more green time
        # - Emergency -> high priority, max green
        # - Bus priority -> moderate priority
        # - Pollution -> may affect (e.g., reduce idling)
        vehicle_factor = min(1.0, state.vehicle_count / 50)
        queue_factor = min(1.0, state.queue_length / 30)
        emergency_factor = 1.0 if state.emergency_status else 0.0
        bus_factor = 0.5 if state.bus_priority else 0.0

        # Base green time in seconds (range 10-60)
        base_green = 15 + 25 * (0.6 * vehicle_factor + 0.4 * queue_factor)
        # Adjust for emergency
        if emergency_factor > 0:
            green_time = 60
            priority = 1.0
            reason = "Emergency vehicle priority"
        elif bus_factor > 0:
            green_time = min(50, base_green * 1.3)
            priority = 0.8
            reason = "Bus priority"
        else:
            green_time = base_green
            priority = 0.3 + 0.5 * (0.6 * vehicle_factor + 0.4 * queue_factor)
            reason = f"Normal traffic: {state.vehicle_count} vehicles, {state.queue_length} queued"

        # Red time = cycle time - green time (assume cycle 60s)
        cycle_time = 60
        red_time = max(5, cycle_time - green_time)
        green_time = min(60, green_time)

        # Confidence based on data freshness and confidence
        confidence = 0.7 + 0.3 * (1 - abs(vehicle_factor - queue_factor))  # more consistent -> higher confidence

        return MasterRecommendation(
            junction_id=state.junction_id,
            green_time=int(green_time),
            red_time=int(red_time),
            priority=round(priority, 2),
            confidence=round(confidence, 2),
            reason=reason,
        )