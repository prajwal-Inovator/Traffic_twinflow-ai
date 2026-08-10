import logging
import os
import sys
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


logger = logging.getLogger("ai_server")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(title="Twinflow AI Service", version="0.1.0")

HOST = os.environ.get("HOST", "0.0.0.0")
try:
    PORT = int(os.environ.get("PORT", "10000"))
except ValueError:
    PORT = 10000


class HealthResponse(BaseModel):
    status: str = "ok"


class PredictRequest(BaseModel):
    junction_id: Optional[str] = None
    current_data: Dict[str, Any]
    horizon_minutes: Optional[int] = 30


class PredictResponse(BaseModel):
    status: str
    result: Dict[str, Any]


class DetectRequest(BaseModel):
    source: str
    options: Optional[Dict[str, Any]] = None


class DetectResponse(BaseModel):
    status: str
    details: Dict[str, Any]


class RecommendRequest(BaseModel):
    junction_id: Optional[str] = None
    current_data: Dict[str, Any]
    target_arrival: Optional[str] = None


class RecommendResponse(BaseModel):
    status: str
    recommendation: Dict[str, Any]


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Twinflow AI service startup initialized")


def import_prediction_engine():
    try:
        from ai.prediction.traffic_predictor import TrafficPredictor
    except Exception as exc:
        logger.exception("Failed to import prediction module")
        raise

    return TrafficPredictor


def import_detection_engine():
    try:
        from ai.detection.main import DetectionEngine
    except Exception as exc:
        logger.exception("Failed to import detection module")
        raise

    return DetectionEngine


def import_recommendation_engine():
    try:
        from ai.recommendation.recommendation_engine import RecommendationEngine
    except Exception as exc:
        logger.exception("Failed to import recommendation module")
        raise

    return RecommendationEngine


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    try:
        import_prediction_engine()
        return PredictResponse(
            status="ok",
            result={
                "message": "prediction endpoint is ready",
                "junction_id": request.junction_id,
                "current_data_keys": list(request.current_data.keys()),
                "horizon_minutes": request.horizon_minutes,
            },
        )
    except Exception as exc:
        logger.exception("Prediction request failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/detect", response_model=DetectResponse)
async def detect(request: DetectRequest) -> DetectResponse:
    try:
        import_detection_engine()
        return DetectResponse(
            status="ok",
            details={
                "message": "detection endpoint is ready",
                "source": request.source,
                "options": request.options or {},
            },
        )
    except Exception as exc:
        logger.exception("Detection request failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest) -> RecommendResponse:
    try:
        import_recommendation_engine()
        return RecommendResponse(
            status="ok",
            recommendation={
                "message": "recommendation endpoint is ready",
                "junction_id": request.junction_id,
                "current_data_keys": list(request.current_data.keys()),
                "target_arrival": request.target_arrival,
            },
        )
    except Exception as exc:
        logger.exception("Recommendation request failed")
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Twinflow AI HTTP service on %s:%s", HOST, PORT)
    uvicorn.run("main:app", host=HOST, port=PORT, log_level="info")
