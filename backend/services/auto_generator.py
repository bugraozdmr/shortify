import asyncio
import json
from datetime import datetime, timezone
from sqlalchemy import select
from loguru import logger

from core.database import SessionLocal
from core.models import Setting
from core.schemas import GenerateRequest
from routers.generate import run_pipeline_task

POLL_INTERVAL = 15
_last_run: datetime | None = None
_semaphore: asyncio.Semaphore | None = None
_running_tasks: set[asyncio.Task] = set()


async def _run_generation():
    logger.info("Otomatik video üretimi başlıyor...")
    try:
        from worker import process_video_task
        request = GenerateRequest(mode="auto")
        # Kuyruğa atıyoruz. Senkron olarak .delay() çağrılır.
        process_video_task.delay(request.model_dump())
        logger.info("Otomatik video üretim isteği Celery kuyruğuna gönderildi.")
    except Exception as e:
        logger.error(f"Otomatik video üretim hatası: {e}")


def _cleanup_done():
    pass # Artık yerel task yönetimi yapmıyoruz


async def auto_generate_loop():
    global _last_run, _semaphore

    _semaphore = asyncio.Semaphore(2)

    while True:
        try:
            async with SessionLocal() as db:
                result = await db.execute(
                    select(Setting).where(Setting.key.in_([
                        "auto_generate_enabled",
                        "auto_generate_interval_hours",
                        "auto_generate_interval_minutes",
                        "auto_generate_max_concurrent",
                    ]))
                )
                rows = result.scalars().all()
                s = {}
                for row in rows:
                    try:
                        s[row.key] = json.loads(row.value)
                    except Exception:
                        s[row.key] = row.value

                enabled = s.get("auto_generate_enabled", False)
                interval_h = int(s.get("auto_generate_interval_hours", 0))
                interval_m = int(s.get("auto_generate_interval_minutes", 30))
                max_concurrent = int(s.get("auto_generate_max_concurrent", 2))

            _semaphore = asyncio.Semaphore(max(max_concurrent, 1))

            if enabled:
                total_interval = interval_h * 3600 + interval_m * 60
                if total_interval <= 0:
                    total_interval = 1800

                now = datetime.now(timezone.utc)
                should_run = (
                    _last_run is None or
                    (now - _last_run).total_seconds() >= total_interval
                )

                if should_run:
                    _cleanup_done()
                    task = asyncio.create_task(_run_generation())
                    _running_tasks.add(task)
                    _last_run = now

        except Exception as e:
            logger.error(f"Auto-generator loop hatası: {e}")

        await asyncio.sleep(POLL_INTERVAL)


_task = None


def start():
    global _task
    if _task is None or _task.done():
        _task = asyncio.create_task(auto_generate_loop())
        logger.info("Otomatik video üretici servisi başlatıldı.")


def stop():
    global _task
    if _task and not _task.done():
        _task.cancel()
    for t in _running_tasks:
        if not t.done():
            t.cancel()
    logger.info("Otomatik video üretici servisi durduruldu.")
