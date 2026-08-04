# services/data_ingestion/main.py
import asyncio
import aiohttp
import logging
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import os

app = FastAPI(title="Data Ingestion Service", version="1.0.0")
logger = logging.getLogger(__name__)

class IngestionConfig(BaseModel):
    sources: list  # e.g., ["openweather", "tavily", "openaq"]

@app.post("/ingest")
async def trigger_ingestion(config: IngestionConfig, background_tasks: BackgroundTasks):
    """Trigger ingestion from configured external APIs."""
    background_tasks.add_task(ingest_all, config.sources)
    return {"status": "started", "sources": config.sources}

async def ingest_all(sources: list):
    """Fetch data from all sources and store in MongoDB."""
    for source in sources:
        if source == "openweather":
            await ingest_weather()
        elif source == "tavily":
            await ingest_tavily()
        elif source == "openaq":
            await ingest_openaq()
        else:
            logger.warning(f"Unknown source: {source}")

async def ingest_weather():
    """Fetch weather data from OpenWeatherMap."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city = os.getenv("CITY", "Delhi")
    if not api_key:
        logger.error("OpenWeather API key missing")
        return
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                logger.info(f"Weather data ingested: {data}")
                # Store in MongoDB (implementation omitted)
            else:
                logger.error(f"Weather API error: {resp.status}")

async def ingest_tavily():
    """Fetch traffic data from Tavily (example)."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.error("Tavily API key missing")
        return
    # Tavily API call – placeholder
    logger.info("Tavily ingestion placeholder")

async def ingest_openaq():
    """Fetch air quality data from OpenAQ."""
    api_key = os.getenv("OPENAQ_API_KEY")
    if not api_key:
        logger.error("OpenAQ API key missing")
        return
    # OpenAQ API call – placeholder
    logger.info("OpenAQ ingestion placeholder")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)