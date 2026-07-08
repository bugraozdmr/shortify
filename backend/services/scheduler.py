import asyncio
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.future import select as future_select
from loguru import logger

from database import SessionLocal
from models import Post
from pipeline.youtube import upload_video_to_youtube

POLL_INTERVAL = 30

async def process_scheduled_posts():
    while True:
        try:
            async with SessionLocal() as db:
                now = datetime.now()
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

                if posts:
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
