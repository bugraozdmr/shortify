import os
import random
import subprocess
from pathlib import Path
from loguru import logger

def get_random_background_video() -> str:
    """Returns the path to a random background video."""
    bg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "backgrounds")
    videos = [f for f in os.listdir(bg_dir) if f.endswith(('.mp4', '.mov'))]
    if not videos:
        raise FileNotFoundError("No background videos found in assets/backgrounds/")
    return os.path.join(bg_dir, random.choice(videos))

def get_music_path(music_name: str) -> str:
    """Returns the path to the background music file."""
    music_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "music")
    # Fuzzy match the music name in case of missing extension
    for f in os.listdir(music_dir):
        if music_name.lower() in f.lower():
            return os.path.join(music_dir, f)
    raise FileNotFoundError(f"Music '{music_name}' not found in assets/music/")

def render_video(bg_video_path: str, bg_music_path: str, voice_audio_path: str, ass_subtitle_path: str, output_path: str):
    """
    Renders the final video using FFmpeg.
    - Loops background video
    - Overlays TTS audio
    - Overlays background music (lowered volume)
    - Burns ASS subtitles
    - Cuts exactly to the TTS audio length
    """
    
    # We must pass absolute paths to ffmpeg filters to avoid escaping issues
    ass_abs = os.path.abspath(ass_subtitle_path)
    # FFmpeg requires escaping colons and backslashes in filter paths
    ass_escaped = ass_abs.replace('\\', '/').replace(':', '\\:')
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", bg_video_path,
        "-i", voice_audio_path,
        "-stream_loop", "-1", "-i", bg_music_path,
        "-filter_complex", 
        f"[0:v]ass='{ass_escaped}'[v];[2:a]volume=0.25[music];[1:a][music]amix=inputs=2:duration=first:dropout_transition=2[a]",
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]
    
    logger.info("Running FFmpeg render...")
    logger.debug("Command: {}", " ".join(cmd))
    
    # Run FFmpeg
    subprocess.run(cmd, check=True)
    
    return output_path
