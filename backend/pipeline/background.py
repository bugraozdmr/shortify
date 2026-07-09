import os
import random
import subprocess
from loguru import logger

def get_media_duration(file_path: str) -> float:
    """ffprobe kullanarak bir medyanın süresini saniye cinsinden döndürür."""
    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        return float(result.stdout.strip())
    except ValueError:
        logger.error(f"Could not get duration for {file_path}")
        return 0.0

def generate_dynamic_background(target_duration: float, output_path: str):
    """
    Belirtilen hedef süreye (target_duration) ulaşana kadar,
    relaxing klasöründeki videolardan rastgele 3-7 saniyelik kesitler alır ve birleştirir.
    """
    logger.info(f"Generating dynamic background video for duration: {target_duration}s")
    base_dir = os.path.dirname(os.path.dirname(__file__))
    relaxing_dir = os.path.join(base_dir, "assets", "backgrounds", "relaxing")
    
    if not os.path.exists(relaxing_dir):
        os.makedirs(relaxing_dir, exist_ok=True)
        
    videos = [f for f in os.listdir(relaxing_dir) if f.endswith(('.mp4', '.mov'))]
    if not videos:
        # Fallback to main backgrounds if relaxing is empty
        relaxing_dir = os.path.join(base_dir, "assets", "backgrounds")
        videos = [f for f in os.listdir(relaxing_dir) if f.endswith(('.mp4', '.mov'))]
        if not videos:
            raise FileNotFoundError("No background videos found in assets/backgrounds/")
            
    accumulated = 0.0
    slices = []
    
    while accumulated < target_duration:
        vid_name = random.choice(videos)
        vid_path = os.path.join(relaxing_dir, vid_name)
        vid_duration = get_media_duration(vid_path)
        
        if vid_duration <= 0:
            continue
            
        # Rastgele slice süresi (3 ile 7 saniye arası)
        slice_duration = random.uniform(3.0, 7.0)
        # Eğer video çok kısaysa videonun kendi süresini al
        if slice_duration > vid_duration:
            slice_duration = vid_duration
            
        # Kalan süreyi aşmamak için kontrol
        if accumulated + slice_duration > target_duration:
            slice_duration = target_duration - accumulated
            
        # Başlangıç zamanı
        max_start = max(0.0, vid_duration - slice_duration)
        start_time = random.uniform(0.0, max_start)
        
        slices.append({
            "path": vid_path,
            "start": start_time,
            "duration": slice_duration
        })
        accumulated += slice_duration

    # FFmpeg komutunu hazırla
    cmd = ["ffmpeg", "-y"]
    
    for s in slices:
        cmd.extend(["-i", s["path"]])
        
    filter_complex = ""
    # Her bir slice için trim, scale, crop ve format (fps vs) standartlaştırma
    # scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280 -> dikey tam ekran, bozulma yok
    # fps=30 -> hepsini 30 fps yap
    # zoompan -> Yavaşça yakınlaşma efekti (z='min(zoom+0.0015,1.5)')
    for i, s in enumerate(slices):
        start = s["start"]
        end = start + s["duration"]
        # zoompan için scale'i biraz büyük başlatıp kesmek yerine, direkt zoompan içinde de yapabiliriz.
        # zoompan için scale'i biraz büyük başlatıp kesmek yerine, direkt zoompan içinde de yapabiliriz.
        # Ama en temizi: Önce 720x1280'e oturt (crop), sonra onun üzerinde yavaş zoom yap.
        slice_duration = s["duration"]
        filter_complex += (
            f"[{i}:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,fps=30,"
            f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
            f"zoompan=z='min(zoom+0.0015,1.5)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280,"
            f"setsar=1:1[v{i}];"
        )
        
    # xfade kullanarak yumuşak geçişler (transition) ekle
    # Tüm geçişler için süre 0.5 saniye
    xfade_duration = 0.5
    
    if len(slices) == 1:
        filter_complex += "[v0]copy[outv]"
    else:
        # İlk offset = ilk videonun süresi - xfade_duration
        current_offset = slices[0]["duration"] - xfade_duration
        last_out = "v0"
        
        for i in range(1, len(slices)):
            next_in = f"v{i}"
            out_name = f"xf{i}" if i < len(slices) - 1 else "outv"
            
            # Rastgele bir geçiş efekti seç (sıkıcılığı önlemek için)
            transitions = ["fade", "wipeleft", "wiperight", "slideup", "slidedown", "smoothleft", "smoothright", "circlecrop", "rectcrop"]
            trans = random.choice(transitions)
            
            filter_complex += f"[{last_out}][{next_in}]xfade=transition={trans}:duration={xfade_duration}:offset={current_offset}[{out_name}];"
            
            # Sonraki offset = mevcut offset + eklenen videonun süresi - xfade_duration
            current_offset += slices[i]["duration"] - xfade_duration
            last_out = out_name
    
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        output_path
    ])
    
    logger.debug(f"Dynamic background FFmpeg command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    return output_path
