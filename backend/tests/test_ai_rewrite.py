import asyncio
import json
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.future import select
from core.database import SessionLocal
from core.models import Setting
from pipeline.ai_rewrite import rewrite_text_for_tiktok
from pipeline.tts import generate_tts

SAMPLE_TEXT = """I work at a grocery store and a few days ago this woman comes in with her son who's about 7 years old. The kid is holding a balloon animal that's all deflated and sad looking. The mom asks me if we have a helium tank to refill it. I told her sorry we don't have one.

She gets all huffy and says "Well what am I supposed to do? He's been crying about this all day." Before I can even respond the kid goes "It's okay mommy, I still love my balloon even if it's a little tired."

The mom just stares at him for a second and then starts BAWLING. Like full on ugly crying in the middle of the store. The kid starts patting her back saying "Don't cry mommy, we can get a new one."

I just stood there holding a bag of potatoes not knowing what to do with my life."""

@pytest.mark.asyncio
async def test_rewrite():
    print("=" * 60)
    print("AI REWRITE TEST")
    print("=" * 60)
    print(f"\nINPUT TEXT:\n{SAMPLE_TEXT[:200]}...\n")

    async with SessionLocal() as db:
        result = await db.execute(select(Setting).where(Setting.key == "api_keys"))
        s = result.scalar_one_or_none()
        api_keys = json.loads(s.value) if s else {}

    result = await rewrite_text_for_tiktok(
        title="I work at a grocery store",
        text=SAMPLE_TEXT,
        provider="gemini",
        model="gemini-2.5-flash",
        api_keys=api_keys
    )

    print("\n" + "=" * 60)
    print("OUTPUT:")
    print("=" * 60)
    print(f"\nTEXT: {result['text']}")
    print(f"\nGENDER: {result['gender']}")
    print(f"\nMUSIC: {result['music']}")
    print(f"\nYT_TITLE: {result['youtube_title']}")
    print(f"\nYT_DESC: {result['youtube_description']}")
    print(f"\nYT_TAGS: {result['youtube_tags']}")
    print("\n" + "=" * 60)
    print(f"TEXT LENGTH: {len(result['text'])} chars, ~{len(result['text'].split())} words")
    print("=" * 60)

    audio_path = f"/tmp/test_tts_{hash(result['text']) % 10000}.mp3"
    await generate_tts(result['text'], audio_path, voice="tr-TR-AhmetNeural")
    print(f"\nTTS kaydedildi: {audio_path} ({os.path.getsize(audio_path)} bytes)")

if __name__ == "__main__":
    asyncio.run(test_rewrite())
