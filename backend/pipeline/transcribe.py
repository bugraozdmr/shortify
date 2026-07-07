import stable_whisper
import os
import ssl

# Workaround for macOS Python SSL certificate download issues
ssl._create_default_https_context = ssl._create_unverified_context

def generate_subtitles(audio_path: str, output_path: str = None) -> str:
    """
    Generates word-level synchronized subtitles (.ass) for the given audio file using stable-ts.
    Outputs an .ass file with TikTok-style karaoke highlighting.
    """
    if not output_path:
        output_path = audio_path.replace('.mp3', '.ass').replace('.wav', '.ass')
        
    print("Loading Whisper model (this may take a moment on first run)...")
    # 'small' model is a good balance between speed and accuracy for Turkish
    model = stable_whisper.load_model('small')
    
    print(f"Transcribing {audio_path}...")
    # Transcribe the audio
    result = model.transcribe(audio_path, language="tr")
    
    print(f"Generating .ass subtitles at {output_path}...")
    
    # Generate Advanced SubStation Alpha file for TikTok-style styling
    # stable-ts natively applies a karaoke effect for word-level sync
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.to_ass(
        output_path,
        font='Impact',          # TikTok ve Shorts'ta sık kullanılan kalın, şık ve okunaklı font
        font_size=20,
        color='&H00FFFFFF',     # Beyaz ana metin
        secondary_color='&H0000FFFF', # Sarı vurgu rengi
        outline=2.5,            # Okunabilirliği artıran kalın siyah kenarlık
        shadow=1.5,             # Hafif gölge derinliği
        karaoke=True            # Kelime kelime vurgulama efekti
    )
    
    return output_path
