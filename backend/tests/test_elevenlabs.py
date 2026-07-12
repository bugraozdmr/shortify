import os
import sys
import pytest
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.elevenlabs import generate_elevenlabs_tts

async def run_standalone():
    api_key = os.environ.get("ELEVENLABS_API_KEY", "your_api_key")
    
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    
    text = "Merhaba! Bu küçük cümle, ElevenLabs seslendirme işlemini test etmek için oluşturulmuştur."
    
    output_dir = os.path.join(os.path.dirname(__file__), "outputs")
    output_path = os.path.join(output_dir, "test_audio.mp3")
    
    print(f"⏳ Seslendirme işlemi başlatılıyor...\nMetin: '{text}'")
    
    result = await generate_elevenlabs_tts(text, output_path, voice_id, api_key)
    
    if result and os.path.exists(result):
        print(f"✅ Başarılı! Ses dosyası oluşturuldu: {result}")
    else:
        print("❌ Ses oluşturulurken bir hata meydana geldi. Detaylar için logları kontrol et.")

@pytest.mark.asyncio
async def test_elevenlabs_tts():
    api_key = os.environ.get("ELEVENLABS_API_KEY", "your_api_key")
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "9q3uhh453wT9R7x3sW1i")

        
    text = "Pytest üzerinden çalışan ElevenLabs seslendirme testi."
    output_path = os.path.join(os.path.dirname(__file__), "outputs", "pytest_audio.mp3")
    
    result = await generate_elevenlabs_tts(text, output_path, voice_id, api_key)
    
    assert result is not None
    assert os.path.exists(result)

if __name__ == "__main__":
    asyncio.run(run_standalone())
