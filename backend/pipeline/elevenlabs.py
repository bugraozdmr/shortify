import os
import ssl
import aiohttp
import aiofiles
from loguru import logger

ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

async def generate_elevenlabs_tts(text: str, output_path: str, voice_id: str, api_key: str) -> str | None:
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        }

        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.35,
                "similarity_boost": 0.75,
                "speed": 1.0,
            },
        }

        url = ELEVENLABS_URL.format(voice_id=voice_id)

        import certifi
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"ElevenLabs API error {resp.status}: {error_text}")
                    return None

                async with aiofiles.open(output_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(8192):
                        await f.write(chunk)

        if os.path.exists(output_path):
            return output_path
        return None

    except Exception as e:
        logger.error(f"ElevenLabs TTS Error: {e}")
        return None
