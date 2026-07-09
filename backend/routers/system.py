from fastapi import APIRouter
import os
from redis.asyncio import Redis
from sqlalchemy import text
from core.database import SessionLocal

router = APIRouter(tags=["System"])

@router.get("/")
def read_root():
    return {"message": "Video Pipeline API Çalışıyor! 🚀 Dökümantasyon için /docs adresine gidin."}

@router.get("/health")
async def health_check():
    health_status = {
        "status": "success",
        "message": "Backend is healthy and running.",
        "services": {
            "database": "unknown",
            "redis": "unknown"
        }
    }
    
    # 1. Veritabanı (MySQL) Kontrolü
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "ok"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
        
    # 2. Redis Kontrolü
    try:
        from utils.config import config
        redis_url = config.REDIS_URL
        client = Redis.from_url(redis_url)
        ping = await client.ping()
        if ping:
            health_status["services"]["redis"] = "ok"
        else:
            health_status["services"]["redis"] = "failed"
        await client.close()
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
        
    return health_status
