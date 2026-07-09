import re
from openai import AsyncOpenAI
from utils.config import config
from loguru import logger

async def _call_gemini(model: str, key: str, prompt: str, content: str, max_retries: int = 3, retry_wait: int = 3) -> str:
    # Celery (ForkPool) + gRPC deadlocks are avoided by using the OpenAI-compatible REST API for Gemini
    client = AsyncOpenAI(
        api_key=key, 
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    import asyncio
    for attempt in range(max_retries):
        try:
            response = await client.chat.completions.create(
                model=model or "gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": content}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            logger.warning(f"[GEMINI] API Error (Attempt {attempt+1}/{max_retries}), retrying in {retry_wait} seconds... Error: {e}")
            await asyncio.sleep(retry_wait)

async def _call_openai_compatible(provider: str, model: str, key: str, prompt: str, content: str, max_retries: int = 3, retry_wait: int = 3) -> str:
    base_url = "https://api.deepseek.com" if provider == "deepseek" else None
    default_model = "gpt-4o-mini" if provider == "openai" else "deepseek-chat"
    
    if not key:
        raise ValueError(f"API key missing for {provider}")
        
    client = AsyncOpenAI(api_key=key, base_url=base_url)
    
    import asyncio
    for attempt in range(max_retries):
        try:
            response = await client.chat.completions.create(
                model=model or default_model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": content}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            logger.warning(f"[{provider.upper()}] API Error (Attempt {attempt+1}/{max_retries}), retrying in {retry_wait} seconds... Error: {e}")
            await asyncio.sleep(retry_wait)

def _parse_ai_response(result_text: str, fallback_title: str) -> dict:
    gender = "female" if "[GENDER: FEMALE]" in result_text.upper() else "male"
    
    music_match = re.search(r'\[MUSIC:(.*?)\]', result_text, flags=re.IGNORECASE)
    music = music_match.group(1).strip() if music_match else "Wii Music"
    
    yt_title_match = re.search(r'\[YT_TITLE:(.*?)\]', result_text, flags=re.IGNORECASE)
    yt_title = yt_title_match.group(1).strip() if yt_title_match else fallback_title
    
    yt_desc_match = re.search(r'\[YT_DESC:(.*?)\]', result_text, flags=re.IGNORECASE)
    yt_desc = yt_desc_match.group(1).strip() if yt_desc_match else ""
    
    yt_tags_match = re.search(r'\[YT_TAGS:(.*?)\]', result_text, flags=re.IGNORECASE)
    yt_tags = yt_tags_match.group(1).strip() if yt_tags_match else "shorts,reddit"
    
    # Clean tags and separator from the text
    clean_text = re.sub(r'\[(GENDER|MUSIC|YT_TITLE|YT_DESC|YT_TAGS):.*?\]', '', result_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'---+\s*', '', clean_text)
    
    # Normalize whitespace
    clean_text = re.sub(r'\n\s*\n', '\n', clean_text)
    clean_text = re.sub(r'  +', ' ', clean_text).strip()
    clean_text = re.sub(r'\n', ' ', clean_text).strip()
    
    return {
        "text": clean_text,
        "gender": gender,
        "music": music,
        "youtube_title": yt_title,
        "youtube_description": yt_desc,
        "youtube_tags": yt_tags
    }

async def rewrite_text_for_tiktok(
    title: str, 
    text: str, 
    provider: str = "gemini",
    model: str = "gemini-2.5-flash",
    api_keys: dict = None,
    max_retries: int = 3,
    retry_wait: int = 3
) -> dict:
    provider = provider.lower()
    api_keys = api_keys or {}
    
    default_prompt = (
        "Sen viral Shorts içerikleri üreten uzman bir sosyal medya yöneticisisin. "
        "Görevin: Verilen hikayeyi, izleyiciyi ilk saniyede yakalayan, akıcı ve doğal bir anlatıma dönüştürmek.\n\n"
        "KURALLAR:\n"
        "1. Birinci tekil şahıs ('Ben') ağzından anlat, olay sanki sen yaşamışsın gibi samimi ve içten ol.\n"
        "2. 20-45 saniye arası (~50-120 kelime). Gereksiz detayları at, doğrudan olaya gir.\n"
        "3. Kanca (hook) ile başla: İzleyiciyi meraklandıracak bir ilk cümle kur.\n"
        "4. Dili doğal ve konuşma diline yakın tut. Karmaşık cümlelerden kaçın.\n"
        "5. ÇOK ÖNEMLİ: Hikayeyi TEK PARAGRAF halinde yaz. Kesinlikle satır atlama, boşluk bırakma. Cümleler art arda düz metin olarak gelsin.\n"
        "6. Cümleler birbirine bağlı aksın, duraklama olmasın. Kesinlikle ... (üç nokta) kullanma.\n"
        "7. Duyguyu hissettir: Şaşkınlık, utanç, korku, komedi — hikayenin türüne göre tonu ayarla.\n"
        "8. Hızlı bir tempoda anlat. Akış sürekli olsun, boşluk ve bekleme olmasın.\n\n"
        "MÜZİK SEÇİMİ (hikayenin havasına en uygun olanı seç):\n"
        "- Sneaky Snitch (Gizem / Komedi, yalan söyleme)\n"
        "- Scheming Weasel Faster (Kaotik Komedi, kavga, absürt olaylar)\n"
        "- Monkeys Spinning Monkeys (Eğlenceli, utandırıcı anılar)\n"
        "- Fluffing a Duck (Hafif Komedi, günlük tatlı hikayeler)\n"
        "- Sneaky Adventure (Macera, keşif)\n"
        "- Investigations (Ciddi Gizem, suç, TIFU, paranormal)\n"
        "- Wii Music (Rahat, sakin anlatımlar)\n"
        "- Wii Shop Channel (Eğlenceli, nostaljik, liste)\n\n"
        "YOUTUBE META VERİLERİ (videoyu sat!):\n"
        "- YT_TITLE: Tıklama oranı yüksek, merak uyandıran, duygusal veya şok edici bir başlık (maks 80 karakter). Başlığın sonuna bizi öne çıkaracak maks 3 adet hashtag ekle (örnek: #shorts #komik #hikaye). Büyük harf ve emoji kullanmaktan çekinme.\n"
        "- YT_DESC: 2-3 satırlık açıklama. İlk satır merak uyandırsın, sonra #hashtag'lerle bitir. Anahtar kelimeleri doğal şekilde yerleştir.\n"
        "- YT_TAGS: 10-15 arası virgülle ayrılmış etiket. Geniş + dar eşleme yap. Örn: shorts, keşfet, hikaye, gerçek hikaye, komik, tifu, itiraf, psikoloji, iş hayatı, ilişkiler, aşk, başarısızlık, ders, pişmanlık, komik anı\n\n"
        "YANIT FORMATI (kesinlikle bu sırayla):\n"
        "[GENDER: MALE veya FEMALE] (Hikayedeki anlatıcının cinsiyetine göre seç)\n"
        "[MUSIC: Müzik Adı]\n"
        "[YT_TITLE: Başlık Buraya]\n"
        "[YT_DESC: Açıklama buraya #hashtag]\n"
        "[YT_TAGS: etiket1, etiket2, etiket3]\n"
        "---\n"
        "En üstteki etiketlerden sonra --- koy ve hemen altına sadece senaryo metnini yaz. Başka hiçbir şey yazma."
    )
    
    full_content = f"BAŞLIK: {title}\n\nHİKAYE:\n{text}"
    
    try:
        if provider == "gemini":
            key = api_keys.get("gemini")
            result_text = await _call_gemini(model, key, default_prompt, full_content, max_retries, retry_wait)
        elif provider in ["openai", "deepseek"]:
            key = api_keys.get(provider)
            result_text = await _call_openai_compatible(provider, model, key, default_prompt, full_content, max_retries, retry_wait)
        else:
            raise ValueError(f"Unknown AI_PROVIDER: {provider}")
            
        return _parse_ai_response(result_text, fallback_title=title)
            
    except Exception as e:
        logger.error(f"[{provider.upper()}] API Error: {e}")
        return None
