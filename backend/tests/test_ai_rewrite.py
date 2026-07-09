import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.config import config
from pipeline.ai_rewrite import rewrite_text_for_tiktok
from core.database import SessionLocal
import sqlalchemy
import json

@pytest.mark.asyncio
async def test_rewrite_text_for_tiktok():
    async with SessionLocal() as db:
        res = await db.execute(sqlalchemy.text("SELECT `key`, value FROM settings WHERE `key` IN ('ai_provider', 'ai_model', 'api_keys')"))
        rows = res.fetchall()
        settings = {}
        for r in rows:
            try:
                settings[r[0]] = json.loads(r[1])
            except:
                settings[r[0]] = r[1]
                
    ai_provider = settings.get("ai_provider", "gemini")
    ai_model = settings.get("ai_model", "gemini-2.5-flash")
    api_keys = settings.get("api_keys", {})
    
    if not api_keys.get(ai_provider):
        pytest.skip(f"API key for {ai_provider} not found in database settings")
        
    sample_title = "TIFU by sending my boss a meme"
    sample_text = "I thought I was sending a meme to my friend but it went to my boss. It was a meme about hating work."
    
    result = await rewrite_text_for_tiktok(
        title=sample_title, 
        text=sample_text, 
        provider=ai_provider,
        model=ai_model,
        api_keys=api_keys
    )
    
    assert result is not None
    assert isinstance(result, dict)
    assert "text" in result
    assert "gender" in result
    assert len(result["text"]) > 0
    
    print("\n" + "="*50)
    print(f"✅ TEST SUCCESSFUL! AI REWRITE ({ai_provider.upper()}):")
    print("="*50)
    print(f"Detected Gender: {result['gender']}")
    print(f"Selected Music:  {result.get('music', 'Unknown')}")
    print("-" * 50)
    print(result["text"])
    print("="*50 + "\n")
