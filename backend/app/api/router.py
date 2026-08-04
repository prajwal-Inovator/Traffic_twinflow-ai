# backend/app/api/router.py
from fastapi import APIRouter
from .v1.endpoints import (
    auth,
    traffic,
    prediction,
    simulation,
    negotiation,
    recommendation,
    emergency,
    notification,
    analytics,
    carbon,
    infrastructure,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
api_router.include_router(traffic.router, prefix="/v1/traffic", tags=["Traffic"])
api_router.include_router(prediction.router, prefix="/v1/prediction", tags=["Prediction"])
api_router.include_router(simulation.router, prefix="/v1/simulation", tags=["Simulation"])
api_router.include_router(negotiation.router, prefix="/v1/negotiation", tags=["Negotiation"])
api_router.include_router(recommendation.router, prefix="/v1/recommendation", tags=["Recommendation"])
api_router.include_router(emergency.router, prefix="/v1/emergency", tags=["Emergency"])
api_router.include_router(notification.router, prefix="/v1/notification", tags=["Notification"])
api_router.include_router(analytics.router, prefix="/v1/analytics", tags=["Analytics"])
api_router.include_router(carbon.router, prefix="/v1/carbon", tags=["Carbon"])
api_router.include_router(infrastructure.router, prefix="/v1/infrastructure", tags=["Infrastructure"])