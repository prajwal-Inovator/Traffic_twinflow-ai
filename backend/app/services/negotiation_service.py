# backend/app/services/negotiation_service.py
import os
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.base import BaseRepository
from ..models.negotiation import MasterRecommendation, NegotiationMessage
from .http_client import ServiceClient


class NegotiationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.rec_repo = BaseRepository[MasterRecommendation](db, "recommendations", MasterRecommendation)
        self.msg_repo = BaseRepository[NegotiationMessage](db, "negotiation_messages", NegotiationMessage)

        self.negotiation_url = os.getenv(
            "NEGOTIATION_SERVICE_URL",
            "http://localhost:8003",
        )
        self.client = ServiceClient(
            self.negotiation_url,
            timeout=60,
            service_name="Negotiation Service",
        )

    async def get_recommendations(
        self,
        junction_id: Optional[str] = None,
    ) -> List[dict]:
        params = {"junction_id": junction_id} if junction_id else None
        return await self.client.request(
            "GET",
            "/recommendations",
            params=params,
        )

    async def create_recommendation(self, rec_data: dict) -> MasterRecommendation:
        return await self.rec_repo.create(rec_data)

    async def store_negotiation_message(self, msg_data: dict) -> NegotiationMessage:
        return await self.msg_repo.create(msg_data)

    async def trigger_negotiation(self, junction_id: str) -> dict:
        return await self.client.request(
            "POST",
            f"/trigger/{junction_id}",
        )
