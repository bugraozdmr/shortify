import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from loguru import logger
from aiogram.client.default import DefaultBotProperties
from sqlalchemy.future import select
from core.database import SessionLocal
from core.models import Setting

async def _get_telegram_settings():
    async with SessionLocal() as db:
        result = await db.execute(select(Setting).where(Setting.key.in_([
            "telegram_bot_token", "telegram_chat_id", "telegram_notification_active"
        ])))
        rows = result.scalars().all()
        settings = {s.key: s.value.strip('"') if isinstance(s.value, str) else s.value for s in rows}
        
        # bool parser for sqlite/json
        active = settings.get("telegram_notification_active", True)
        if isinstance(active, str):
            active = active.lower() == "true"
            
        return {
            "token": settings.get("telegram_bot_token", ""),
            "chat_id": settings.get("telegram_chat_id", ""),
            "active": active
        }

async def _get_bot(token: str) -> Bot | None:
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN yapılandırılmamış (DB'de boş), Telegram mesajı gönderilemiyor.")
        return None
    return Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def send_video_success_notification(post_title: str, video_path: str):
    settings = await _get_telegram_settings()
    
    if not settings["active"]:
        return
        
    chat_id = settings["chat_id"]
    if not chat_id:
        logger.warning("TELEGRAM_CHAT_ID yapılandırılmamış (DB'de boş), mesaj atlanıyor.")
        return
        
    bot = await _get_bot(settings["token"])
    if not bot:
        return
        
    try:
        caption = (
            f"✅ <b>Yeni Video Üretildi!</b>\n\n"
            f"<b>Hikaye:</b> {post_title}\n\n"
            f"<i>Video başarıyla oluşturuldu ve render edildi.</i>"
        )
        
        # Eğer gelecekte buton vs. eklenmek istenirse buraya InlineKeyboardMarkup eklenebilir.
        # reply_markup = InlineKeyboardMarkup(...)
        
        video_file = FSInputFile(video_path)
        await bot.send_video(chat_id=chat_id, video=video_file, caption=caption)
        logger.info(f"Telegram'a başarılı üretim mesajı gönderildi: {post_title}")
    except Exception as e:
        logger.error(f"Telegram'a başarı mesajı gönderilirken hata oluştu: {e}")
    finally:
        await bot.session.close()

async def send_error_notification(post_title: str, error_message: str):
    settings = await _get_telegram_settings()
    
    if not settings["active"]:
        return
        
    chat_id = settings["chat_id"]
    if not chat_id:
        logger.warning("TELEGRAM_CHAT_ID yapılandırılmamış (DB'de boş), hata mesajı atlanıyor.")
        return
        
    bot = await _get_bot(settings["token"])
    if not bot:
        return
        
    try:
        text = (
            f"❌ <b>Boru Hattı Hatası (Video Üretilemedi)</b>\n\n"
            f"<b>Hikaye:</b> {post_title}\n"
            f"<b>Hata Mesajı:</b> <code>{error_message}</code>\n\n"
            f"<i>Lütfen sistemi kontrol edin.</i>"
        )
        
        await bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"Telegram'a hata bildirimi gönderildi: {post_title}")
    except Exception as e:
        logger.error(f"Telegram'a hata mesajı gönderilirken hata oluştu: {e}")
    finally:
        await bot.session.close()
