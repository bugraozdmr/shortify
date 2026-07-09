import asyncio
from core.database import engine
from sqlalchemy import text
from loguru import logger
from routers.settings import get_settings
from core.database import SessionLocal

async def main():
    logger.info("Veritabanı işlemleri başlatılıyor...")
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE settings ADD PRIMARY KEY (`key`)"))
            logger.info("✅ 'settings' tablosuna PRIMARY KEY başarıyla eklendi.")
    except Exception as e:
        logger.warning(f"PRIMARY KEY eklenirken bir hata oluştu (Zaten ekli olabilir): {e}")

    async with SessionLocal() as db:
        await get_settings(db=db)
        logger.info("✅ Tüm yeni varsayılan (default) ayarlar veritabanına başarıyla eklendi!")

if __name__ == "__main__":
    asyncio.run(main())
