import asyncio
import pytest
import os
import sys

# Add the backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.schemas import GenerateRequest
from routers.generate import run_pipeline_task

@pytest.mark.asyncio
async def test_full_auto_pipeline():
    """
    Tüm sistemi uçtan uca (End-to-End) test eder:
    1. Reddit'ten hikaye çeker.
    2. AI (Gemini) ile yeniden yazar.
    3. Ses sentezi (TTS) yapar.
    4. Whisper ile altyazı (Ass) çıkarır.
    5. FFmpeg ile video (mp4) renderlar.
    """
    print("\n[TEST] Uçtan uca otomatik video üretim hattı başlatılıyor...")
    
    video_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "videos")
    # Eski test videolarını temizle
    for f in os.listdir(video_dir):
        if f.startswith("short_") and f.endswith(".mp4"):
            os.remove(os.path.join(video_dir, f))
            
    req = GenerateRequest(mode="auto")
    
    # Tüm boru hattını çalıştır
    await run_pipeline_task(req)
    
    # İşlem bittikten sonra assets/videos klasöründe short_ ile başlayan yeni bir mp4 var mı kontrol et
    videos = [f for f in os.listdir(video_dir) if f.startswith("short_") and f.endswith(".mp4")]
    
    assert len(videos) > 0, "Video üretilemedi!"
    
    latest_video = sorted([os.path.join(video_dir, v) for v in videos], key=os.path.getmtime)[-1]
    
    print("\n" + "="*50)
    print("✅ UÇTAN UCA SİSTEM TESTİ BAŞARILI!")
    print(f"Üretilen Video: {latest_video}")
    print("="*50 + "\n")
