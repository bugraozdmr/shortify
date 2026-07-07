import pytest
import os
from pipeline.render import render_video
from pipeline.tts import generate_tts
from pipeline.transcribe import generate_subtitles

@pytest.mark.asyncio
async def test_full_video_pipeline():
    """
    Test the full video generation pipeline: TTS -> Transcribe -> Render
    """
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "audio")
    video_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "videos")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)
    
    voice_path = os.path.join(audio_dir, "test_pipeline.mp3")
    ass_path = os.path.join(audio_dir, "test_pipeline.ass")
    output_video = os.path.join(video_dir, "test_output.mp4")
    
    text = "Selam! Bugün size harika bir hikaye anlatacağım. Bu video tamamen otomatik üretildi."
    
    # 1. Generate TTS
    print("Generating TTS...")
    await generate_tts(text=text, output_path=voice_path)
    assert os.path.exists(voice_path)
    
    # 2. Generate Subtitles
    print("Generating Subtitles...")
    generate_subtitles(audio_path=voice_path, output_path=ass_path)
    assert os.path.exists(ass_path)
    
    # 3. Render Video
    print("Rendering Video...")
    music_name = "Wii Music" # Using a valid music name
    render_video(voice_audio_path=voice_path, ass_subtitle_path=ass_path, music_name=music_name, output_path=output_video)
    
    assert os.path.exists(output_video)
    file_size = os.path.getsize(output_video)
    assert file_size > 0
    
    print("\n" + "="*50)
    print("✅ TEST SUCCESSFUL! FULL VIDEO RENDERED:")
    print("="*50)
    print(f"Path: {output_video}")
    print(f"Size: {file_size / (1024*1024):.2f} MB")
    print("="*50 + "\n")
