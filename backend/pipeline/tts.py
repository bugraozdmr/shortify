import edge_tts
import os
from loguru import logger


async def generate_tts(text: str, output_path: str, voice: str = "tr-TR-AhmetNeural"):
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        communicate = edge_tts.Communicate(text, voice, rate="+10%")
        await communicate.save(output_path)

        if os.path.exists(output_path):
            return output_path
        else:
            return None
    except Exception as e:
        logger.error(f"TTS Generation Error: {e}")
        return None
