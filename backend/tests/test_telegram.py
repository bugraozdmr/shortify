import sys
import os
import pytest
from loguru import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.telegram_bot import send_error_notification
from utils.config import config

@pytest.mark.asyncio
async def test_telegram_notification():
    logger.info("Telegram Testi Başlatılıyor...")
    
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        pytest.fail("HATA: .env dosyanızda TELEGRAM_BOT_TOKEN veya TELEGRAM_CHAT_ID eksik!")

    logger.info(f"Kullanılan Chat ID: {config.TELEGRAM_CHAT_ID}")
    
    try:
        await send_error_notification(
            post_title="TEST HİKAYESİ (BAŞARILI)", 
            error_message="Bu mesaj Pytest üzerinden gönderildi. Telegram bot altyapısı KUSURSUZ çalışıyor! 🎉"
        )
        logger.info("Test mesajı gönderme fonksiyonu başarıyla çalıştı.")
    except Exception as e:
        pytest.fail(f"Test mesajı gönderilirken bir hata oluştu: {e}")
