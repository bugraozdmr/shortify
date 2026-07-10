import stable_whisper
import os
import ssl
from loguru import logger

ssl._create_default_https_context = ssl._create_unverified_context

def generate_subtitles(audio_path: str, output_path: str = None, original_text: str = None) -> str:
    if not output_path:
        output_path = audio_path.replace('.mp3', '.ass').replace('.wav', '.ass')
        
    logger.info("Loading Whisper model (this may take a moment on first run)...")
    model = stable_whisper.load_model('small')
    
    logger.info(f"Transcribing {audio_path}...")
    # original_text verilmişse initial_prompt olarak kullan ki model saçmalamasın
    result = model.transcribe(audio_path, language="tr", initial_prompt=original_text)
    
    # Kelimeleri parçala (Ekranda aynı anda max 2-3 kelime görünsün - TikTok style)
    try:
        result.split_by_length(max_words=2, max_chars=15)
    except Exception as e:
        logger.warning(f"Could not split by length: {e}")
    
    logger.info(f"Generating .ass subtitles at {output_path}...")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.to_ass(
        output_path,
        font='Archivo Black',
        font_size=20,           
        color='&H00FFFFFF',     
        highlight_color='&H000066FF',
        outline=5,
        shadow=3,               
        karaoke=True,
        word_level=True,
        Alignment=5,            
        Bold=False
    )
    
    return output_path
