import asyncio
from celery import Celery
from core.schemas import GenerateRequest
from routers.generate import run_pipeline_task
from loguru import logger
from utils.config import config

# Redis URL yapılandırması
REDIS_URL = config.REDIS_URL

# Celery uygulamasını oluştur
celery_app = Celery(
    "video_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_concurrency=2, # Aynı anda en fazla 2 video işlensin
    result_expires=3600,  # Redis'te biriken görev sonuçlarını 1 saat sonra otomatik sil
)

@celery_app.task(name="process_video_task")
def process_video_task(request_dict: dict):
    """
    Celery tarafından çalıştırılacak olan senkron görev.
    İçerisinde asenkron olan 'run_pipeline_task' fonksiyonunu çalıştırır.
    """
    logger.info(f"Celery task başladı. Mod: {request_dict.get('mode')}")
    try:
        # Dictionary'den pydantic modelini oluştur
        request = GenerateRequest(**request_dict)
        
        # Asenkron pipeline'ı yeni bir event loop'ta çalıştır
        asyncio.run(run_pipeline_task(request))
        
        logger.info("Celery task başarıyla tamamlandı.")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Celery task hatası: {e}")
        return {"status": "failed", "error": str(e)}
