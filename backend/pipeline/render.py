import os
import random
import subprocess
import json
import shutil
from pathlib import Path
from loguru import logger
from loguru import logger

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

def render_video(bg_music_path: str, voice_audio_path: str, ass_subtitle_path: str, output_path: str, title_text: str = None, channel_name: str = "Anlatsana", comments: list = None):
    from pipeline.background import get_media_duration, generate_dynamic_background
    
    ass_abs = os.path.abspath(ass_subtitle_path)
    ass_escaped = ass_abs.replace('\\', '/').replace(':', '\\:')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Kanal ismi artık argüman olarak geliyor
    
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
    cmd.extend([
        "-i", temp_bg_path,
        "-i", voice_audio_path,
        "-stream_loop", "-1", "-i", bg_music_path
    ])
    
    fonts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts")
    fonts_dir_escaped = fonts_dir.replace('\\', '/').replace(':', '\\:')
    
    input_index = 3
    filter_complex = f"[0:v]ass='{ass_escaped}':fontsdir='{fonts_dir_escaped}',{drawtext_filter}[v_base];"
    last_v = "[v_base]"
    
    if title_text:
        cmd.extend(["-i", card_path])
        filter_complex += f"{last_v}[{input_index}:v]overlay=(W-w)/2:(H-h)/2:enable='between(t,0,4)'[v_title];"
        last_v = "[v_title]"
        input_index += 1
        
    comment_card_paths = []
    audio_mix_inputs = ["[1:a]", "[music]"] # voice, bg_music
    num_audio_inputs = 2
    
    if comments and len(comments) > 0:
        from pipeline.card_generator import generate_comment_card
        base_dir = os.path.dirname(os.path.dirname(__file__))
        vine_boom_path = os.path.join(base_dir, "assets", "music", "funny", "vine_boom.mp3")
        
        # Saniyeleri hesapla
        # Örnek: Videonun 30% - 50% arasında 1. yorum, 70% - 90% arasında 2. yorum
        for i, c in enumerate(comments[:2]):
            c_path = os.path.join(base_dir, "assets", "images", f"temp_comment_{i}.png")
            generate_comment_card(c["author"], c["text"], c_path)
            comment_card_paths.append(c_path)
            
            if i == 0:
                start_t = voice_duration * 0.3
                end_t = voice_duration * 0.5
            else:
                start_t = voice_duration * 0.7
                end_t = voice_duration * 0.9
                
            cmd.extend(["-i", c_path])
            
            next_v = f"[v_c{i}]"
            # Ortalamak yerine biraz alta veya yana koyabiliriz. Y ekseninde ortaya koyalım.
            filter_complex += f"{last_v}[{input_index}:v]overlay=(W-w)/2:(H-h)/2+200:enable='between(t,{start_t},{end_t})'{next_v};"
            last_v = next_v
            input_index += 1
            
            if os.path.exists(vine_boom_path):
                cmd.extend(["-i", vine_boom_path])
                # Ses gecikmesi ms cinsinden
                delay_ms = int(start_t * 1000)
                next_a = f"[a_boom{i}]"
                filter_complex += f"[{input_index}:a]volume=0.8,adelay={delay_ms}|{delay_ms}{next_a};"
                audio_mix_inputs.append(next_a)
                input_index += 1
                num_audio_inputs += 1

    # Outro Card
    outro_start_t = max(0, voice_duration - 2.0)
    outro_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "images", "temp_outro.png")
    
    from pipeline.card_generator import generate_outro_card
    generate_outro_card(channel_name, outro_path)
    
    cmd.extend(["-i", outro_path])
    next_v = "[v_outro]"
    filter_complex += f"{last_v}[{input_index}:v]overlay=(W-w)/2:(H-h)/2:enable='between(t,{outro_start_t},{voice_duration})'{next_v};"
    last_v = next_v
    input_index += 1

    # Rename last video stream to [v]
    filter_complex += f"{last_v}copy[v];"
    
    # Audio mix
    amix_str = "".join(audio_mix_inputs)
    filter_complex += (
        f"[2:a]volume=0.45[music];"
        f"{amix_str}amix=inputs={num_audio_inputs}:duration=first:dropout_transition=2[a]"
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
    for c_path in comment_card_paths:
        if os.path.exists(c_path):
            try:
                os.remove(c_path)
            except:
                pass
    if os.path.exists(outro_path):
        try:
            os.remove(outro_path)
        except:
            pass
            
    return output_path
