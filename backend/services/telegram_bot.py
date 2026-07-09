import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from loguru import logger
from utils.config import config
from aiogram.client.default import DefaultBotProperties

async def _get_bot() -> Bot | None:
    token = config.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN yapılandırılmamış, Telegram mesajı gönderilemiyor.")
        return None
    return Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def send_video_success_notification(post_title: str, video_path: str):
    chat_id = config.TELEGRAM_CHAT_ID
    if not chat_id:
        logger.warning("TELEGRAM_CHAT_ID yapılandırılmamış, mesaj atlanıyor.")
        return
        
    bot = await _get_bot()
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
    chat_id = config.TELEGRAM_CHAT_ID
    if not chat_id:
        logger.warning("TELEGRAM_CHAT_ID yapılandırılmamış, hata mesajı atlanıyor.")
        return
        
    bot = await _get_bot()
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
