# backend/app/api/v1/endpoints/notification.py
from fastapi import APIRouter, Depends
from ....api.deps import get_db, get_current_active_user
from ....services.notification_service import NotificationService

router = APIRouter()

@router.post("/alert")
async def send_alert(user_id: str, message: str, channel: str = "email", db=Depends(get_db)):
    service = NotificationService(db)
    success = await service.send_alert(user_id, message, channel)
    return {"success": success}
    