# services/external_apis/wrappers.py
import aiohttp
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class WeatherAPI:
    """Wrapper for OpenWeatherMap API."""
    BASE_URL = "http://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")

    async def get_current_weather(self, city: str = "Delhi") -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("OpenWeather API key missing")
        url = f"{self.BASE_URL}/weather?q={city}&appid={self.api_key}&units=metric"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(f"Weather API error: {resp.status}")
                    return {}

class TavilyAPI:
    """Wrapper for Tavily API (traffic data)."""
    BASE_URL = "https://api.tavily.com"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")

    async def get_traffic_data(self, location: str = "Delhi") -> Dict[str, Any]:
        # Placeholder – implement according to Tavily docs
        return {"status": "placeholder", "location": location}

class OpenAQAPI:
    """Wrapper for OpenAQ API (air quality)."""
    BASE_URL = "https://api.openaq.org/v2"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAQ_API_KEY")

    async def get_air_quality(self, city: str = "Delhi") -> Dict[str, Any]:
        url = f"{self.BASE_URL}/measurements?city={city}&limit=1"
        headers = {"X-API-Key": self.api_key} if self.api_key else {}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(f"OpenAQ API error: {resp.status}")
                    return {}