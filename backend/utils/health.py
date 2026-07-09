import shutil
import sys
import redis.asyncio as redis
from core.database import SessionLocal
from sqlalchemy import text
from utils.config import config
from loguru import logger

async def check_dependencies():
    missing_deps = False
    
    # 1. FFmpeg & FFprobe Control
    if not shutil.which("ffmpeg"):
        logger.error("KRİTİK HATA: FFmpeg bulunamadı! Video işleme özellikleri çalışmayacaktır.")
        missing_deps = True
    if not shutil.which("ffprobe"):
        logger.error("KRİTİK HATA: FFprobe bulunamadı!")
        missing_deps = True
        
    # 2. Database Connection Control
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"KRİTİK HATA: Veritabanı bağlantısı kurulamadı: {e}")
        missing_deps = True
        
    # 3. Redis Connection Control
    try:
        r = redis.from_url(config.REDIS_URL)
        await r.ping()
        await r.close()
    except Exception as e:
        logger.error(f"KRİTİK HATA: Redis bağlantısı kurulamadı: {e}")
        missing_deps = True
        
    if missing_deps:
        logger.error("Gerekli yazılımlar eksik olduğu için sistem başlatılamıyor. Lütfen hataları giderin.")
        sys.exit(1)
    
    logger.info("Tüm sistem gereksinimleri (Veritabanı, Redis, FFmpeg) başarıyla doğrulandı.")
