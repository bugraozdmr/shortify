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
        raise e

@celery_app.task(name="upload_video_task")
def upload_video_task(post_id: int):
    """
    Celery tarafından çalıştırılacak YouTube yükleme görevi.
    """
    import asyncio
    from sqlalchemy.future import select
    from core.database import SessionLocal
    from core.models import Post
    from pipeline.youtube import upload_video_to_youtube
    from datetime import datetime
    
    logger.info(f"Celery YouTube Yükleme task başladı. Post ID: {post_id}")
    
    async def _do_upload():
        async with SessionLocal() as db:
            result = await db.execute(select(Post).where(Post.id == post_id))
            post = result.scalar_one_or_none()
            
            if not post:
                logger.error(f"Video bulunamadı. Post ID: {post_id}")
                return
                
            try:
                tags = []
                if post.youtube_tags:
                    tags = [t.strip() for t in post.youtube_tags.split(",") if t.strip()]

                # Run sync function in thread
                video_id = await asyncio.to_thread(
                    upload_video_to_youtube,
                    post.video_path,
                    post.youtube_title or post.title,
                    post.youtube_description or "",
                    tags,
                    publish_at=post.scheduled_at
                )

                post.youtube_video_id = video_id
                post.youtube_url = f"https://youtu.be/{video_id}"
                post.youtube_status = "uploaded"
                post.published_at = datetime.now()
                # scheduled_at'i sıfırlamıyoruz ki UI'da ne zamana planlandığı görünsün.
                
                logger.info(f"[{post.id}] YouTube'a başarıyla yüklendi: {post.youtube_url}")
                await db.commit()
                
            except Exception as e:
                logger.error(f"[{post.id}] Celery YouTube yükleme hatası: {e}")
                post.youtube_status = "failed"
                post.error_message = f"YouTube upload failed (Celery): {str(e)}"
                await db.commit()
                raise e

    try:
        asyncio.run(_do_upload())
        return {"status": "success", "post_id": post_id}
    except Exception as e:
        logger.error(f"Upload task fail: {e}")
        raise e
