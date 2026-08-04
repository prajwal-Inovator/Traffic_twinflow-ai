# backend/app/services/carbon_service.py
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..repositories.base import BaseRepository
from ..models.carbon_report import CarbonReport
from datetime import datetime

class CarbonService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = BaseRepository[CarbonReport](db, "carbon_reports", CarbonReport)

    async def get_reports(self, from_date: Optional[datetime] = None, to_date: Optional[datetime] = None) -> List[CarbonReport]:
        filter = {}
        if from_date or to_date:
            filter["date"] = {}
            if from_date:
                filter["date"]["$gte"] = from_date
            if to_date:
                filter["date"]["$lte"] = to_date
        return await self.repo.get_many(filter, limit=100)

    async def create_report(self, report_data: dict) -> CarbonReport:
        return await self.repo.create(report_data)