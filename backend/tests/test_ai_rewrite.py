import pytest
import os
from pipeline.ai_rewrite import rewrite_text_for_tiktok

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")

@pytest.mark.asyncio
async def test_rewrite_text_for_tiktok():
    if AI_PROVIDER == "gemini" and not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not found in .env")
    elif AI_PROVIDER == "openai" and not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not found in .env")
    elif AI_PROVIDER == "deepseek" and not os.getenv("DEEPSEEK_API_KEY"):
        pytest.skip("DEEPSEEK_API_KEY not found in .env")
        
    sample_title = "TIFU by sending my boss a meme"
    sample_text = "I thought I was sending a meme to my friend but it went to my boss. It was a meme about hating work."
    
    result = await rewrite_text_for_tiktok(title=sample_title, text=sample_text)
    
    assert result is not None
    assert isinstance(result, dict)
    assert "text" in result
    assert "voice" in result
    assert len(result["text"]) > 0
    
    print("\n" + "="*50)
    print(f"✅ TEST SUCCESSFUL! AI REWRITE ({AI_PROVIDER.upper()}):")
    print("="*50)
    print(f"Detected Gender: {result['gender']}")
    print(f"Selected Voice:  {result['voice']}")
    print(f"Selected Music:  {result.get('music', 'Unknown')}")
    print("-" * 50)
    print(result["text"])
    print("="*50 + "\n")
