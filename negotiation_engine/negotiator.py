# negotiation_engine/negotiator.py
import asyncio
import logging
from typing import List, Dict, Optional
from .junction_agent import JunctionAgent
from .master_agent import MasterAgent
from .message_broker import broker

logger = logging.getLogger(__name__)

class Negotiator:
    """
    Orchestrates the entire negotiation process:
    - Creates junction agents and master agent.
    - Starts/stops the negotiation cycle.
    - Handles external triggers (e.g., emergency, manual intervention).
    """

    def __init__(self):
        self.junction_agents: Dict[str, JunctionAgent] = {}
        self.master_agent = MasterAgent()
        self.is_running = False

    def register_junction(
        self,
        junction_id: str,
        neighbors: List[str] = None,
        initial_state: Optional[Dict] = None
    ):
        """Register a junction to be managed."""
        if junction_id in self.junction_agents:
            logger.warning(f"Junction {junction_id} already registered.")
            return
        agent = JunctionAgent(junction_id, neighbors, initial_state)
        self.junction_agents[junction_id] = agent

    async def start(self):
        """Start all agents and the master."""
        self.is_running = True
        # Start master
        await self.master_agent.start()

        # Start junction agents
        for agent in self.junction_agents.values():
            await agent.start()

        logger.info(f"Negotiator started with {len(self.junction_agents)} junctions.")

    async def stop(self):
        self.is_running = False
        await self.master_agent.stop()
        for agent in self.junction_agents.values():
            await agent.stop()
        logger.info("Negotiator stopped.")

    async def trigger_negotiation(self, junction_id: Optional[str] = None):
        """Manually trigger a negotiation round for a specific junction or all."""
        if junction_id:
            if junction_id in self.junction_agents:
                # Force a state update and then recommendation
                await self.junction_agents[junction_id].publish_state()
                await self.master_agent.compute_recommendations(junction_id)
            else:
                logger.warning(f"Junction {junction_id} not found.")
        else:
            # Trigger for all
            for agent in self.junction_agents.values():
                await agent.publish_state()
            await self.master_agent.compute_recommendations()

    def get_recommendation(self, junction_id: str) -> Optional[MasterRecommendation]:
        """Get the latest recommendation for a junction."""
        return self.master_agent.last_recommendations.get(junction_id)