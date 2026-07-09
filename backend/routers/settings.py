from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import get_db
from core.models import Setting
from core.schemas import SettingsPayload
from fastapi.responses import PlainTextResponse
import os

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/logs")
async def get_logs():
    log_path = "logs/app.log"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            return PlainTextResponse(f.read())
    return PlainTextResponse("Log dosyası henüz oluşturulmadı veya boş.")

import json

DEFAULTS = {
    "is_auto_upload": False,
    "allowed_upload_start_time": "18:00",
    "allowed_upload_end_time": "22:00",
    "ai_provider": "gemini",
    "ai_model": "gemini-2.5-flash",
    "api_keys": {"gemini": "", "openai": "", "deepseek": "", "openrouter": ""},
    "auto_generate_enabled": False,
    "auto_generate_interval_hours": 0,
    "auto_generate_interval_minutes": 30,
    "auto_generate_max_concurrent": 2,
    "ai_max_retries": 3,
    "ai_retry_wait_seconds": 3,
    "reddit_fetch_max_pages": 5,
    "system_cleanup_older_than_days": 1,
    "channel_name": "Anlatsana",
    "telegram_bot_token": "",
    "telegram_chat_id": "",
    "telegram_notification_active": True,
    "youtube_client_id": "",
    "youtube_client_secret": "",
    "youtube_redirect_uri": "http://localhost:8080/",
    "youtube_max_uploads_per_day": 3
}
CATEGORIES = {
    "is_auto_upload": "Pipeline",
    "allowed_upload_start_time": "Pipeline",
    "allowed_upload_end_time": "Pipeline",
    "ai_provider": "AI",
    "ai_model": "AI",
    "api_keys": "AI",
    "auto_generate_enabled": "Pipeline",
    "auto_generate_interval_hours": "Pipeline",
    "auto_generate_interval_minutes": "Pipeline",
    "auto_generate_max_concurrent": "Pipeline",
    "ai_max_retries": "AI",
    "ai_retry_wait_seconds": "AI",
    "reddit_fetch_max_pages": "Pipeline",
    "system_cleanup_older_than_days": "System",
    "channel_name": "System",
    "telegram_bot_token": "System",
    "telegram_chat_id": "System",
    "telegram_notification_active": "System",
    "youtube_client_id": "System",
    "youtube_client_secret": "System",
    "youtube_redirect_uri": "System",
    "youtube_max_uploads_per_day": "Pipeline"
}


@router.get("/", response_model=SettingsPayload)
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Setting))
    rows = result.scalars().all()
    existing = {s.key: s for s in rows}

    out_dict = {}
    for k, default_val in DEFAULTS.items():
        if k in existing:
            try:
                out_dict[k] = json.loads(existing[k].value)
            except Exception:
                out_dict[k] = existing[k].value
        else:
            db.add(Setting(key=k, value=json.dumps(default_val), category=CATEGORIES.get(k)))
            out_dict[k] = default_val

    if set(existing.keys()) != set(DEFAULTS.keys()):
        await db.commit()

    return out_dict

@router.put("/", response_model=SettingsPayload)
async def update_settings(settings_data: SettingsPayload, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Setting))
    existing_settings = {s.key: s for s in result.scalars().all()}
    
    for key, value in settings_data.items():
        if key in existing_settings:
            existing_settings[key].value = json.dumps(value)
        else:
            db.add(Setting(key=key, value=json.dumps(value)))
            
    await db.commit()
    
    # Güncel halini döndür
    result = await db.execute(select(Setting))
    out_dict = {}
    for s in result.scalars().all():
        try:
            out_dict[s.key] = json.loads(s.value)
        except Exception:
            out_dict[s.key] = s.value
            
    return out_dict
