import os
import random
import subprocess
import json
import shutil
from pathlib import Path
from loguru import logger
from utils.config import config

def get_random_background_video() -> str:
    bg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "backgrounds")
    videos = [f for f in os.listdir(bg_dir) if f.endswith(('.mp4', '.mov'))]
    if not videos:
        raise FileNotFoundError("No background videos found in assets/backgrounds/")
    return os.path.join(bg_dir, random.choice(videos))

def get_music_path(music_name: str) -> str:
    music_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "music")
    for f in os.listdir(music_dir):
        if music_name.lower() in f.lower():
            return os.path.join(music_dir, f)
    raise FileNotFoundError(f"Music '{music_name}' not found in assets/music/")

def render_video(bg_music_path: str, voice_audio_path: str, ass_subtitle_path: str, output_path: str, title_text: str = None):
    from pipeline.background import get_media_duration, generate_dynamic_background
    
    ass_abs = os.path.abspath(ass_subtitle_path)
    ass_escaped = ass_abs.replace('\\', '/').replace(':', '\\:')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Kanal ismini .env'den al (eğer yoksa Shortify yazsın)
    channel_name = config.get("CHANNEL_NAME", "Shortify")
    
    # "Parıltılı" ve kalın (Bold) efekti: 
    drawtext_filter = f"drawtext=font='Arial Rounded MT Bold':text='{channel_name}':fontcolor=white@0.85:fontsize=56:x=(w-text_w)/2:y=h-200:borderw=3:bordercolor=white@0.3:shadowcolor=white@0.2:shadowx=4:shadowy=4"
    
    # Intro kartını oluştur
    card_path = ""
    cmd = ["ffmpeg", "-y"]
    
    if title_text:
        from pipeline.card_generator import generate_social_card
        base_dir = os.path.dirname(os.path.dirname(__file__))
        logo_path = os.path.join(base_dir, "assets", "images", "logo.png")
        card_path = os.path.join(base_dir, "assets", "images", "temp_card.png")
        generate_social_card(logo_path, channel_name, title_text, card_path)
    
    # Ses uzunluğunu bul ve arka planı dinamik olarak oluştur
    voice_duration = get_media_duration(voice_audio_path)
    # Ses çok kısaysa (örn testler) minimum 5 saniye video üret
    if voice_duration < 5.0:
        voice_duration = 5.0
        
    # xfade geçişleri toplam süreyi kısalttığı için fazladan 5 saniye buffer (pay) bırakıyoruz
    bg_target_duration = voice_duration + 5.0
        
    temp_bg_path = os.path.join(os.path.dirname(output_path), "temp_dynamic_bg.mp4")
    generate_dynamic_background(target_duration=bg_target_duration, output_path=temp_bg_path)
    
    # Input 0: Dinamik Video, Input 1: Voice, Input 2: Music
    # Artık video zaten tam sese göre kesildiği için -stream_loop'a gerek yok
    cmd.extend([
        "-i", temp_bg_path,
        "-i", voice_audio_path,
        "-stream_loop", "-1", "-i", bg_music_path
    ])
    
    if title_text:
        # Input 3: Card image
        cmd.extend(["-i", card_path])
        
        # [0:v] (bg_video) üzerine ass ve drawtext ekle -> [v_text]
        # [v_text] üzerine [3:v] (kart) ekle (overlay) -> [v]
        filter_complex = (
            f"[0:v]ass='{ass_escaped}',{drawtext_filter}[v_text];"
            f"[v_text][3:v]overlay=(W-w)/2:(H-h)/2:enable='between(t,0,4)'[v];"
            f"[2:a]volume=0.45[music];"
            f"[1:a][music]amix=inputs=2:duration=first:dropout_transition=2[a]"
        )
    else:
        filter_complex = (
            f"[0:v]ass='{ass_escaped}',{drawtext_filter}[v];"
            f"[2:a]volume=0.45[music];"
            f"[1:a][music]amix=inputs=2:duration=first:dropout_transition=2[a]"
        )
        
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "-t", str(voice_duration),
        output_path
    ])
    
    logger.info("Running FFmpeg render...")
    logger.debug("Command: {}", " ".join(cmd))
    
    subprocess.run(cmd, check=True)
    
    # Temizlik
    if card_path and os.path.exists(card_path):
        try:
            os.remove(card_path)
        except:
            pass
            
    return output_path
