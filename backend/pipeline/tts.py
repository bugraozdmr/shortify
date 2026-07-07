import edge_tts
import os

async def generate_tts(text: str, output_path: str, voice: str = "tr-TR-AhmetNeural"):
    """
    Generates a TTS audio file from the provided text using edge-tts.
    The default voice is set to a Turkish male voice (tr-TR-AhmetNeural).
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        
        if os.path.exists(output_path):
            return output_path
        else:
            return None
    except Exception as e:
        print(f"TTS Generation Error: {e}")
        return None

# List of available Turkish voices (for reference):
# tr-TR-AhmetNeural (Male)
# tr-TR-EmelNeural (Female)
