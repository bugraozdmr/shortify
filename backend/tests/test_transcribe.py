import pytest
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.transcribe import generate_subtitles

def test_generate_subtitles():
    audio_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "audio", "test_audio.mp3")
    
    if not os.path.exists(audio_path):
        pytest.skip(f"Test audio not found at {audio_path}. Run test_tts.py first.")
        
    output_path = audio_path.replace('.mp3', '.ass')
    
    result_path = generate_subtitles(audio_path=audio_path, output_path=output_path)
    
    assert result_path is not None
    assert os.path.exists(result_path)
    
    file_size = os.path.getsize(result_path)
    assert file_size > 0, "Generated subtitle file is empty!"
    
    print("\n" + "="*50)
    print("✅ TEST SUCCESSFUL! SUBTITLES GENERATED:")
    print("="*50)
    print(f"Path: {result_path}")
    print(f"Size: {file_size} bytes")
    print("="*50 + "\n")
