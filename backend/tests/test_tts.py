import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.tts import generate_tts

@pytest.mark.asyncio
async def test_generate_tts():
    sample_text = "Merhaba Şeyma annen seni sevmiyor"
    
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "audio")
    os.makedirs(audio_dir, exist_ok=True)
    output_path = os.path.join(audio_dir, "test_audio.mp3")
    
    result_path = await generate_tts(text=sample_text, output_path=output_path)
    
    assert result_path is not None
    assert os.path.exists(result_path)
    
    # Check if the file is not empty (size > 0 bytes)
    file_size = os.path.getsize(result_path)
    assert file_size > 0, "Generated TTS audio file is empty!"
    
    print("\n" + "="*50)
    print("✅ TEST SUCCESSFUL! TTS AUDIO GENERATED:")
    print("="*50)
    print(f"Path: {result_path}")
    print(f"Size: {file_size} bytes")
    print("="*50 + "\n")
