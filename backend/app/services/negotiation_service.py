# backend/app/services/negotiation_service.py
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..repositories.base import BaseRepository
from ..models.negotiation import MasterRecommendation, NegotiationMessage
from ..core.exceptions import NotFoundError
from negotiation_engine.negotiator import Negotiator

class NegotiationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.negotiator = Negotiator()
        # Register junctions from DB (or from digital twin)
        # This will be done in an init method.

    async def initialize(self):
        """Register all junctions from the database."""
        # Fetch all junctions from DB (signals collection)
        signals = await self.signal_repo.get_many({})
        for signal in signals:
            jid = signal.junction_id
            # We need neighbors; for now, we can leave empty or load from road topology
            self.negotiator.register_junction(jid, neighbors=[])
        # Start negotiator
        await self.negotiator.start()

    async def trigger_negotiation(self, junction_id: str) -> dict:
        await self.negotiator.trigger_negotiation(junction_id)
        return {"negotiation_id": f"neg_{datetime.utcnow().timestamp()}", "junction_id": junction_id}

    async def get_recommendations(self, junction_id: Optional[str] = None) -> List[MasterRecommendation]:
        if junction_id:
            rec = self.negotiator.get_recommendation(junction_id)
            return [rec] if rec else []
        else:
            # Return all recommendations
            return list(self.negotiator.master_agent.last_recommendations.values())

class NegotiationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.rec_repo = BaseRepository[MasterRecommendation](db, "recommendations", MasterRecommendation)
        self.msg_repo = BaseRepository[NegotiationMessage](db, "negotiation_messages", NegotiationMessage)

    async def get_recommendations(self, junction_id: Optional[str] = None) -> List[MasterRecommendation]:
        filter = {}
        if junction_id:
            filter["junction_id"] = junction_id
        return await self.rec_repo.get_many(filter, limit=50)

    async def create_recommendation(self, rec_data: dict) -> MasterRecommendation:
        return await self.rec_repo.create(rec_data)

    async def store_negotiation_message(self, msg_data: dict) -> NegotiationMessage:
        return await self.msg_repo.create(msg_data)

    async def trigger_negotiation(self, junction_id: str) -> dict:
        """Placeholder: triggers negotiation process."""
        # In later steps, this will call the AI agent
        return {"negotiation_id": f"neg_{datetime.utcnow().timestamp()}", "junction_id": junction_id}

from datetime import datetime