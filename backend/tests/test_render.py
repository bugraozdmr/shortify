import pytest
import os
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.render import render_video
from pipeline.tts import generate_tts
from pipeline.transcribe import generate_subtitles

@pytest.mark.asyncio
async def test_full_video_pipeline():
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "audio")
    video_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "videos")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)
    
    voice_path = os.path.join(audio_dir, "test_pipeline.mp3")
    ass_path = os.path.join(audio_dir, "test_pipeline.ass")
    output_video = os.path.join(video_dir, "test_output.mp4")
    
    text = "Merhabalar! Bu bir sistem testidir. Yeni dinamik arka planlarımız ve karaoke tipi yanan sarı altyazılarımız harika görünüyor! Videolarımızın dikkat çekeceğinden hiç şüphemiz yok. Hemen başlayalım!"
    
    # 1. Generate TTS
    print("Generating TTS...")
    await generate_tts(text=text, output_path=voice_path)
    assert os.path.exists(voice_path)
    
    # 2. Generate Subtitles
    print("Generating Subtitles...")
    generate_subtitles(audio_path=voice_path, output_path=ass_path, original_text=text)
    assert os.path.exists(ass_path)
    
    # 3. Render Video
    print("Rendering Video...")
    from pipeline.render import get_music_path
    bg_music = get_music_path("Wii Music")
    render_video(
        bg_music_path=bg_music,
        voice_audio_path=voice_path,
        ass_subtitle_path=ass_path,
        output_path=output_video,
        title_text=text
    )
    assert os.path.exists(output_video)
    file_size = os.path.getsize(output_video)
    assert file_size > 0
    
    print("\n" + "="*50)
    print("✅ TEST SUCCESSFUL! FULL VIDEO RENDERED:")
    print("="*50)
    print(f"Path: {output_video}")
    print(f"Size: {file_size / (1024*1024):.2f} MB")
    print("="*50 + "\n")
