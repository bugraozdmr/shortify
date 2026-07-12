from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from loguru import logger
from core.schemas import GenerateRequest
import asyncio
import os
import re
import uuid

# Import the standalone pipeline modules
from pipeline.fetcher import fetch_best_posts
from pipeline.ai_rewrite import rewrite_text_for_tiktok, translate_comments
from pipeline.tts import generate_tts
from pipeline.elevenlabs import generate_elevenlabs_tts
from pipeline.transcribe import generate_subtitles
from pipeline.render import render_video, get_random_background_video, get_music_path
from services.telegram_bot import send_video_success_notification, send_error_notification

# Import Database tools for the background task
from core.database import SessionLocal, get_db
from core.models import Post, PostStatus, Setting

router = APIRouter(prefix="/generate", tags=["Generate"])

async def _get_settings(db: AsyncSession) -> dict:
    import json
    result = await db.execute(select(Setting))
    setting_rows = result.scalars().all()
    settings_dict = {}
    for s in setting_rows:
        try:
            settings_dict[s.key] = json.loads(s.value)
        except:
            settings_dict[s.key] = s.value
    return settings_dict

async def _prepare_post(request: GenerateRequest, settings: dict, db: AsyncSession):
    if request.mode == "manual":
        if not request.custom_text:
            raise Exception("Manuel modda custom_text gönderilmelidir.")
        original_text = request.custom_text
        post_title = "Özel Metin"
        source_id = str(uuid.uuid4())
        source = "manual"
        subreddit = None
        comments = []
    else:
        source = "reddit"
        subreddit = "tifu"
        
        existing_query = await db.execute(select(Post.source_id).filter(Post.source == source))
        existing_ids = set(existing_query.scalars().all())
        
        max_pages = settings.get("reddit_fetch_max_pages", 5)
        posts = await fetch_best_posts(subreddit, limit=1, existing_ids=existing_ids, max_pages=max_pages)
        
        if not posts:
            raise Exception("Tüm popüler hikayeler zaten çekilmiş. Yeni hikaye bulunamadı (Max 5 sayfa tarandı).")
            
        selected_post = posts[0]
        
        original_text = selected_post["text"]
        post_title = selected_post["title"]
        source_id = selected_post["reddit_id"]
        comments = selected_post.get("comments", [])
        
    db_post = Post(
        source=source,
        source_id=source_id,
        subreddit=subreddit,
        title=post_title,
        comments=comments,
        status=PostStatus.processing
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post, original_text, post_title

async def _run_ai_step(db_post: Post, post_title: str, original_text: str, settings: dict, db: AsyncSession):
    ai_provider = settings.get("ai_provider", "gemini")
    ai_model = settings.get("ai_model", "gemini-2.5-flash")
    api_keys = settings.get("api_keys", {})
    max_retries = settings.get("ai_max_retries", 3)
    retry_wait = settings.get("ai_retry_wait_seconds", 3)
    
    logger.info(f"[{db_post.id}] AI ile yeniden yazılıyor...")
    ai_result = await rewrite_text_for_tiktok(
        title=post_title, 
        text=original_text, 
        provider=ai_provider,
        model=ai_model,
        api_keys=api_keys,
        max_retries=max_retries,
        retry_wait=retry_wait
    )
    if not ai_result:
        raise Exception("Yapay zeka metni oluşturamadı.")
    
    ai_text = ai_result["text"]
    ai_text = re.sub(r'\n\s*\n+', ' ', ai_text)
    ai_text = re.sub(r'\n', ' ', ai_text)
    ai_text = re.sub(r'  +', ' ', ai_text).strip()
    ai_text = ai_text.replace('...', '').replace('..', '')
    ai_result["text"] = ai_text

    db_post.youtube_title = ai_result.get("youtube_title")
    db_post.youtube_description = ai_result.get("youtube_description")
    db_post.youtube_tags = ai_result.get("youtube_tags")
    
    if db_post.comments:
        logger.info(f"[{db_post.id}] Yorumlar Türkçeye çevriliyor...")
        translated_comments = await translate_comments(
            comments=db_post.comments,
            provider=ai_provider,
            model=ai_model,
            api_keys=api_keys,
            max_retries=max_retries,
            retry_wait=retry_wait
        )
        db_post.comments = translated_comments
        
    await db.commit()
    return ai_result

async def _run_media_step(db_post: Post, ai_result: dict, settings: dict, db: AsyncSession):
    gender = ai_result.get("gender", "male")
    elevenlabs_key = settings.get("elevenlabs_api_key", "")
        
    music_name = ai_result.get("music", "Wii Music")
    ai_text = ai_result["text"]
    
    audio_path = f"assets/audio/voice_{db_post.id}.wav"
    voice = "tr-TR-EmelNeural" if gender == "female" else "tr-TR-AhmetNeural"
    logger.info(f"[{db_post.id}] Ses sentezi (edge-tts) yapılıyor (Ses: {voice})...")
    await generate_tts(ai_text, audio_path, voice=voice)

    logger.info(f"[{db_post.id}] Altyazı (.ass) üretiliyor...")
    ass_path = f"assets/subtitles/sub_{db_post.id}.ass"
    await asyncio.to_thread(generate_subtitles, audio_path, ass_path, ai_text)

    logger.info(f"[{db_post.id}] Video oluşturuluyor...")
    bg_music = get_music_path(music_name) or get_music_path("Wii Music")
    final_video_path = f"assets/videos/short_{db_post.id}.mp4"
    
    title_for_card = db_post.youtube_title or db_post.title
    if db_post.youtube_title:
        title_for_card = re.sub(r'#\w+', '', db_post.youtube_title).strip()
        title_for_card = title_for_card or db_post.youtube_title
        
    title_for_card = re.sub(r'[^\w\s.,!?\'"\-:]', '', title_for_card).strip()
    
    channel_name = settings.get("channel_name", "Anlatsana")
    await asyncio.to_thread(render_video, bg_music, audio_path, ass_path, final_video_path, title_text=title_for_card, channel_name=channel_name, comments=db_post.comments)

    db_post.video_path = final_video_path
    db_post.status = PostStatus.completed
    await db.commit()
    logger.info(f"[{db_post.id}] Tüm boru hattı başarıyla tamamlandı: {final_video_path}")
    
    await send_video_success_notification(post_title=db_post.title, video_path=final_video_path)

async def run_pipeline_task(request: GenerateRequest):
    async with SessionLocal() as db:
        try:
            settings = await _get_settings(db)
            db_post, original_text, post_title = await _prepare_post(request, settings, db)
            ai_result = await _run_ai_step(db_post, post_title, original_text, settings, db)
            await _run_media_step(db_post, ai_result, settings, db)
            
        except Exception as e:
            logger.error(f"Boru hattı hatası: {e}")
            if 'db_post' in locals():
                title_for_err = db_post.title
                # Başarısız olan işlemleri (ister reddit, ister manuel) 
                # veritabanında tutmaya gerek yok, direkt siliyoruz.
                await db.delete(db_post)
                await db.commit()
                await send_error_notification(post_title=title_for_err, error_message=str(e))
            else:
                await send_error_notification(post_title="Bilinmeyen Hikaye (Hazırlık Aşaması)", error_message=str(e))
            raise e


@router.post("/")
async def generate_video(request: GenerateRequest, db: AsyncSession = Depends(get_db)):
    # Celery task'ını çalıştır.
    # request.model_dump() veya dict(request) diyerek sözlüğe çevirip gönderiyoruz.
    from worker import process_video_task
    
    process_video_task.delay(request.model_dump())
    
    return {
        "message": "Video üretim işlemi kuyruğa (Celery) eklendi. Arka planda işleniyor.",
        "status": "processing"
    }
