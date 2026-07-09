import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select, and_, delete
from sqlalchemy.future import select as future_select
from loguru import logger

from core.database import SessionLocal
from core.models import Post, Setting
from pipeline.youtube import upload_video_to_youtube

POLL_INTERVAL = 30

async def process_scheduled_posts():
    while True:
        try:
            async with SessionLocal() as db:
                now = datetime.now()
                
                # --- CLEANUP TASK ---
                # 1 günden eski olan ve hala 'processing' statüsünde takılı kalmış kayıtları sil
                # Veritabanından dinamik olarak okuyoruz
                setting_res = await db.execute(select(Setting).where(Setting.key == "system_cleanup_older_than_days"))
                setting_val = setting_res.scalar_one_or_none()
                days_to_keep = 1
                if setting_val:
                    try:
                        days_to_keep = int(setting_val.value)
                    except Exception:
                        pass
                        
                cutoff_time = now - timedelta(days=days_to_keep)
                delete_stmt = delete(Post).where(
                    and_(
                        Post.status == "processing",
                        Post.created_at < cutoff_time
                    )
                )
                await db.execute(delete_stmt)
                
                # --- SCHEDULED UPLOAD TASK ---
                result = await db.execute(
                    select(Post).where(
                        and_(
                            Post.scheduled_at.isnot(None),
                            Post.scheduled_at <= now,
                            Post.youtube_status == "pending",
                            Post.status == "completed",
                            Post.video_path.isnot(None),
                            Post.deleted_at.is_(None)
                        )
                    )
                )
                posts = result.scalars().all()

                for post in posts:
                    try:
                        logger.info(f"[{post.id}] Zamanlanmış YouTube yüklemesi başlıyor...")

                        tags = []
                        if post.youtube_tags:
                            tags = [t.strip() for t in post.youtube_tags.split(",") if t.strip()]

                        video_id = await asyncio.to_thread(
                            upload_video_to_youtube,
                            post.video_path,
                            post.youtube_title or post.title,
                            post.youtube_description or "",
                            tags,
                        )

                        post.youtube_video_id = video_id
                        post.youtube_url = f"https://youtu.be/{video_id}"
                        post.youtube_status = "uploaded"
                        post.published_at = datetime.now()
                        post.scheduled_at = None

                        logger.info(f"[{post.id}] YouTube'a yüklendi: {post.youtube_url}")

                    except Exception as e:
                        logger.error(f"[{post.id}] YouTube yükleme hatası: {e}")
                        post.youtube_status = "failed"
                        post.error_message = f"YouTube upload failed: {str(e)}"

                await db.commit()

        except Exception as e:
            logger.error(f"Scheduler hatası: {e}")

        await asyncio.sleep(POLL_INTERVAL)


scheduler_task = None

def start_scheduler():
    global scheduler_task
    if scheduler_task is None or scheduler_task.done():
        scheduler_task = asyncio.create_task(process_scheduled_posts())
        logger.info("Zamanlanmış yayınlama servisi başlatıldı.")

def stop_scheduler():
    global scheduler_task
    if scheduler_task and not scheduler_task.done():
        scheduler_task.cancel()
        logger.info("Zamanlanmış yayınlama servisi durduruldu.")
