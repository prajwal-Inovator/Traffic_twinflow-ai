# services/data_ingestion/ingestion_service.py
import asyncio
import logging
from typing import Dict, Any, Optional
import httpx
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class DataIngestionService:
    """Fetch real-time data from external APIs and store in database."""

    def __init__(self, db, api_keys: Dict[str, str]):
        self.db = db
        self.api_keys = api_keys
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch_openweather(self, lat: float, lng: float) -> Dict[str, Any]:
        """Fetch current weather from OpenWeather."""
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lng,
            "appid": self.api_keys.get("openweather"),
            "units": "metric",
        }
        try:
            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "weather": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "openweather",
            }
        except Exception as e:
            logger.error(f"OpenWeather fetch failed: {e}")
            return {}

    async def fetch_openaq(self, lat: float, lng: float) -> Dict[str, Any]:
        """Fetch air quality data from OpenAQ."""
        url = "https://api.openaq.org/v2/latest"
        params = {
            "coordinates": f"{lat},{lng}",
            "radius": 1000,
            "limit": 1,
        }
        headers = {"X-API-Key": self.api_keys.get("openaq", "")}
        try:
            resp = await self.client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            if data["results"]:
                result = data["results"][0]
                measurements = {m["parameter"]: m["value"] for m in result["measurements"]}
                return {
                    "aqi": measurements.get("pm25", 0),
                    "pm25": measurements.get("pm25", 0),
                    "pm10": measurements.get("pm10", 0),
                    "no2": measurements.get("no2", 0),
                    "o3": measurements.get("o3", 0),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "source": "openaq",
                }
            return {}
        except Exception as e:
            logger.error(f"OpenAQ fetch failed: {e}")
            return {}

    async def fetch_tavily(self, query: str) -> Dict[str, Any]:
        """Fetch news/events from Tavily API."""
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.api_keys.get("tavily"),
            "query": query,
            "search_depth": "basic",
            "include_answer": True,
        }
        try:
            resp = await self.client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return {
                "answer": data.get("answer"),
                "results": data.get("results", []),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "tavily",
            }
        except Exception as e:
            logger.error(f"Tavily fetch failed: {e}")
            return {}

    async def ingest_all(self, lat: float, lng: float, query: str = "traffic news") -> Dict[str, Any]:
        """Ingest data from all sources."""
        weather, air_quality, news = await asyncio.gather(
            self.fetch_openweather(lat, lng),
            self.fetch_openaq(lat, lng),
            self.fetch_tavily(query),
            return_exceptions=True
        )
        return {
            "weather": weather if not isinstance(weather, Exception) else {},
            "air_quality": air_quality if not isinstance(air_quality, Exception) else {},
            "news": news if not isinstance(news, Exception) else {},
            "ingested_at": datetime.utcnow().isoformat() + "Z",
        }

    async def close(self):
        await self.client.aclose()