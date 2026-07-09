import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select, and_, delete
from sqlalchemy.future import select as future_select
from loguru import logger

from core.database import SessionLocal
from core.models import Post, Setting
from core.models import Post, Setting
from worker import upload_video_task

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

                # 2. AYAR OKUMA: Max yükleme limiti
                setting_res = await db.execute(select(Setting).where(Setting.key == "youtube_max_uploads_per_day"))
                setting_val = setting_res.scalar_one_or_none()
                max_uploads = 3
                if setting_val:
                    try:
                        max_uploads = int(setting_val.value)
                    except Exception:
                        pass
                        
                # 3. BUGÜNKÜ YÜKLEMELER
                start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
                today_uploads_res = await db.execute(
                    select(Post).where(
                        and_(
                            Post.youtube_status == "uploaded",
                            Post.published_at >= start_of_day
                        )
                    )
                )
                today_uploads_count = len(today_uploads_res.scalars().all())

                for post in posts:
                    try:
                        if today_uploads_count >= max_uploads:
                            # Bugün limit dolmuş. Videoyu bir gün sonraya ötele.
                            post.scheduled_at = post.scheduled_at + timedelta(days=1)
                            logger.info(f"[{post.id}] Günlük YouTube yükleme limitine ({max_uploads}) ulaşıldı. Video yarına ötelendi: {post.scheduled_at}")
                            continue

                        logger.info(f"[{post.id}] Zamanlanmış YouTube yüklemesi kuyruğa atılıyor (Celery)...")

                        # Celery kuyruğuna gönderiyoruz
                        upload_video_task.delay(post.id)

                        # Durumu "uploading" yaparak tekrar alınmasını engelliyoruz
                        post.youtube_status = "uploading"
                        today_uploads_count += 1
                        
                        logger.info(f"[{post.id}] Celery kuyruğuna iletildi.")

                    except Exception as e:
                        logger.error(f"[{post.id}] Kuyruğa atılırken hata oluştu: {e}")
                        post.youtube_status = "failed"
                        post.error_message = f"Queueing failed: {str(e)}"

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
