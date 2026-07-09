import os
import re
import google.generativeai as genai
from openai import AsyncOpenAI
from utils.config import config
from loguru import logger

async def rewrite_text_for_tiktok(
    title: str, 
    text: str, 
    provider: str = "gemini",
    model: str = "gemini-2.5-flash",
    api_keys: dict = None
) -> dict:
    if api_keys is None:
        api_keys = {}
        
    provider = provider.lower()
    
    # Configure API Keys dynamically
    gemini_model = None
    openai_client = None
    
    if provider == "gemini":
        key = api_keys.get("gemini") or os.getenv("GEMINI_API_KEY", "")
        if key:
            genai.configure(api_key=key)
        if not model:
            model = 'gemini-2.5-flash'
        gemini_model = genai.GenerativeModel(model)
        
    elif provider in ["openai", "deepseek"]:
        key = api_keys.get(provider) or (os.getenv("OPENAI_API_KEY") if provider == "openai" else os.getenv("DEEPSEEK_API_KEY"))
        base_url = "https://api.deepseek.com" if provider == "deepseek" else None
        if not model:
            model = "gpt-4o-mini" if provider == "openai" else "deepseek-chat"
        
        if not key:
            raise ValueError(f"API key missing for {provider}")
            
        openai_client = AsyncOpenAI(api_key=key, base_url=base_url)

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
        "[GENDER: MALE]\n"
        "[MUSIC: Müzik Adı]\n"
        "[YT_TITLE: Başlık Buraya]\n"
        "[YT_DESC: Açıklama buraya #hashtag]\n"
        "[YT_TAGS: etiket1, etiket2, etiket3]\n"
        "---\n"
        "En üstteki etiketlerden sonra --- koy ve hemen altına sadece senaryo metnini yaz. Başka hiçbir şey yazma."
    )
    
    full_content = f"BAŞLIK: {title}\n\nHİKAYE:\n{text}"
    
    try:
        result_text = ""
        if provider == "gemini":
            response = gemini_model.generate_content([default_prompt, full_content])
            result_text = response.text.strip()
            
        elif provider in ["openai", "deepseek"]:
            response = await openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": default_prompt},
                    {"role": "user", "content": full_content}
                ],
                temperature=0.7
            )
            result_text = response.choices[0].message.content.strip()
            
        else:
            raise ValueError(f"Unknown AI_PROVIDER: {provider}")
        
        # Parse Gender Tag
        gender = "male" # default
        if "[GENDER: FEMALE]" in result_text.upper():
            gender = "female"
            
        # Parse Music Tag
        music = "Wii Music" # default
        music_match = re.search(r'\[MUSIC:(.*?)\]', result_text, flags=re.IGNORECASE)
        if music_match:
            music = music_match.group(1).strip()
            
        # Parse YouTube Tags
        yt_title = title # fallback
        yt_title_match = re.search(r'\[YT_TITLE:(.*?)\]', result_text, flags=re.IGNORECASE)
        if yt_title_match:
            yt_title = yt_title_match.group(1).strip()
            
        yt_desc = ""
        yt_desc_match = re.search(r'\[YT_DESC:(.*?)\]', result_text, flags=re.IGNORECASE)
        if yt_desc_match:
            yt_desc = yt_desc_match.group(1).strip()
            
        yt_tags = "shorts,reddit"
        yt_tags_match = re.search(r'\[YT_TAGS:(.*?)\]', result_text, flags=re.IGNORECASE)
        if yt_tags_match:
            yt_tags = yt_tags_match.group(1).strip()
            
        # Clean tags and separator from the text
        result_text = re.sub(r'\[GENDER:.*?\]', '', result_text, flags=re.IGNORECASE).strip()
        result_text = re.sub(r'\[MUSIC:.*?\]', '', result_text, flags=re.IGNORECASE).strip()
        result_text = re.sub(r'\[YT_TITLE:.*?\]', '', result_text, flags=re.IGNORECASE).strip()
        result_text = re.sub(r'\[YT_DESC:.*?\]', '', result_text, flags=re.IGNORECASE).strip()
        result_text = re.sub(r'\[YT_TAGS:.*?\]', '', result_text, flags=re.IGNORECASE).strip()
        result_text = re.sub(r'---+\s*', '', result_text).strip()
        # Normalize whitespace: collapse multiple newlines/spaces for clean TTS output
        result_text = re.sub(r'\n\s*\n', '\n', result_text).strip()
        result_text = re.sub(r'  +', ' ', result_text).strip()
        result_text = re.sub(r'\n', ' ', result_text).strip()
            
        voice = "tr-TR-EmelNeural" if gender == "female" else "tr-TR-AhmetNeural"
        
        return {
            "text": result_text,
            "voice": voice,
            "gender": gender,
            "music": music,
            "youtube_title": yt_title,
            "youtube_description": yt_desc,
            "youtube_tags": yt_tags
        }
            
    except Exception as e:
        logger.error(f"[{provider.upper()}] API Error: {e}")
        return None
