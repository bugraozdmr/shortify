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
from pipeline.ai_rewrite import rewrite_text_for_tiktok
from pipeline.tts import generate_tts
from pipeline.transcribe import generate_subtitles
from pipeline.render import render_video, get_random_background_video, get_music_path

# Import Database tools for the background task
from core.database import SessionLocal, get_db
from core.models import Post, PostStatus, Setting

router = APIRouter(prefix="/generate", tags=["Generate"])

async def run_pipeline_task(request: GenerateRequest):
    # Background task içinde kullanılmak üzere yeni bir session açıyoruz
    async with SessionLocal() as db:
        try:
            import json
            # 1. AYARLARI ÇEK
            result = await db.execute(select(Setting))
            setting_rows = result.scalars().all()
            settings_dict = {}
            for s in setting_rows:
                try:
                    settings_dict[s.key] = json.loads(s.value)
                except:
                    settings_dict[s.key] = s.value
                    
            ai_provider = settings_dict.get("ai_provider", "gemini")
            ai_model = settings_dict.get("ai_model", "gemini-2.5-flash")
            api_keys = settings_dict.get("api_keys", {})
            
            # 2. HİKAYEYİ BELİRLE (Manuel vs Otomatik)
            post_title = "Otomatik Seçilen Hikaye"
            original_text = ""
            source_id = str(uuid.uuid4()) # Varsayılan unique id
            source = "manual"
            subreddit = None

            if request.mode == "manual":
                if not request.custom_text:
                    raise Exception("Manuel modda custom_text gönderilmelidir.")
                # Manuel Mod
                original_text = request.custom_text
                post_title = "Özel Metin"
            else:
                # Otomatik Mod (Reddit)
                source = "reddit"
                subreddit = "tifu"
                posts = await fetch_best_posts(subreddit, limit=30)
                
                selected_post = None
                for p in posts:
                    # Veritabanında daha önce bu reddit_id (source_id) var mı?
                    existing = await db.execute(select(Post).filter(Post.source_id == p['reddit_id']))
                    if not existing.scalars().first():
                        selected_post = p
                        break
                
                if not selected_post:
                    raise Exception("Tüm popüler hikayeler zaten çekilmiş. Yeni hikaye bulunamadı.")
                
                original_text = selected_post["text"]
                post_title = selected_post["title"]
                source_id = selected_post["reddit_id"]
            
            # 3. VERİTABANINA KAYDET (Status: processing)
            db_post = Post(
                source=source,
                source_id=source_id,
                subreddit=subreddit,
                title=post_title,
                status=PostStatus.processing
            )
            db.add(db_post)
            await db.commit()
            await db.refresh(db_post)

            # 4. AI REWRITE
            logger.info(f"[{db_post.id}] AI ile yeniden yazılıyor...")
            ai_result = await rewrite_text_for_tiktok(
                title=post_title, 
                text=original_text, 
                provider=ai_provider,
                model=ai_model,
                api_keys=api_keys
            )
            if not ai_result:
                raise Exception("Yapay zeka metni oluşturamadı.")
            
            ai_text = ai_result["text"]
            # Normalize whitespace: collapse all newlines and extra spaces
            ai_text = re.sub(r'\n\s*\n+', ' ', ai_text)
            ai_text = re.sub(r'\n', ' ', ai_text)
            ai_text = re.sub(r'  +', ' ', ai_text).strip()
            # Remove ellipses and long pauses for continuous flow
            ai_text = ai_text.replace('...', '')
            ai_text = ai_text.replace('..', '')

            voice = ai_result["voice"]
            music_name = ai_result["music"]

            db_post.youtube_title = ai_result.get("youtube_title")
            db_post.youtube_description = ai_result.get("youtube_description")
            db_post.youtube_tags = ai_result.get("youtube_tags")
            await db.commit()

            # 5. TTS (SES SENTEZİ)
            logger.info(f"[{db_post.id}] Ses sentezi (TTS) yapılıyor...")
            audio_path = f"assets/audio/voice_{db_post.id}.wav"
            await generate_tts(ai_text, audio_path, voice=voice)

            # 6. ALTYAZI (TRANSCRIBE)
            logger.info(f"[{db_post.id}] Altyazı (.ass) üretiliyor...")
            ass_path = f"assets/subtitles/sub_{db_post.id}.ass"
            # generate_subtitles senkron olduğu için to_thread kullanıyoruz
            await asyncio.to_thread(generate_subtitles, audio_path, ass_path, ai_text)

            # 7. RENDER (VİDEO OLUŞTURMA)
            logger.info(f"[{db_post.id}] Video oluşturuluyor...")
            bg_music = get_music_path(music_name)
            if not bg_music:
                bg_music = get_music_path("Wii Music") # Fallback
                
            final_video_path = f"assets/videos/short_{db_post.id}.mp4"
            
            # Kart başlığı için Türkçe üretilmiş youtube_title'ı kullanalım, yoksa orijinali kalsın
            if db_post.youtube_title:
                # Hashtag'leri (#shorts vb.) temizle
                clean_title = re.sub(r'#\w+', '', db_post.youtube_title).strip()
                title_for_card = clean_title if clean_title else db_post.youtube_title
            else:
                title_for_card = db_post.title
                
            # Emoji ve desteklenmeyen karakterleri temizle (Sadece harf, rakam, temel noktalama)
            # \w harf/rakam/altçizgi, \s boşluk. Özel Türkçe karakterleri \w zaten yakalar.
            title_for_card = re.sub(r'[^\w\s.,!?\'"\-:]', '', title_for_card).strip()
            
            # render_video da senkron
            await asyncio.to_thread(render_video, bg_music, audio_path, ass_path, final_video_path, title_text=title_for_card)

            # 8. SONUÇ
            db_post.video_path = final_video_path
            db_post.status = PostStatus.completed
            await db.commit()
            
            logger.info(f"[{db_post.id}] Tüm boru hattı başarıyla tamamlandı: {final_video_path}")

        except Exception as e:
            logger.error(f"[{db_post.id if 'db_post' in locals() else '?'}] Boru hattı hatası: {e}")
            if 'db_post' in locals():
                db_post.status = PostStatus.failed
                db_post.error_message = str(e)
                await db.commit()


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
