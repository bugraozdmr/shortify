import os
import google.generativeai as genai
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Supported: "gemini", "openai", "deepseek"
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
AI_MODEL = os.getenv("AI_MODEL")

# Globals for clients
gemini_model = None
openai_client = None

if AI_PROVIDER == "gemini":
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
    if not AI_MODEL:
        AI_MODEL = 'gemini-1.5-flash'
    gemini_model = genai.GenerativeModel(AI_MODEL)

elif AI_PROVIDER in ["openai", "deepseek"]:
    api_key = os.getenv("OPENAI_API_KEY") if AI_PROVIDER == "openai" else os.getenv("DEEPSEEK_API_KEY")
    base_url = "https://api.deepseek.com" if AI_PROVIDER == "deepseek" else None
    
    if not AI_MODEL:
        AI_MODEL = "gpt-4o-mini" if AI_PROVIDER == "openai" else "deepseek-chat"
        
    openai_client = AsyncOpenAI(api_key=api_key, base_url=base_url)

import re

async def rewrite_text_for_tiktok(title: str, text: str, custom_prompt: str = None) -> dict:
    """
    Rewrites a Reddit post into a catchy TikTok/Shorts script.
    Uses custom_prompt if provided, otherwise defaults to a pre-defined prompt.
    Supports Gemini, OpenAI (GPT), and DeepSeek.
    """
    default_prompt = (
        "Sen viral içerik üreten uzman bir sosyal medya yöneticisisin. "
        "Aşağıda verilen Reddit hikayesini TikTok ve YouTube Shorts formatına uygun, "
        "kısa, kancalı (hook içeren), sürükleyici ve akıcı bir senaryoya dönüştür. "
        "ÇOK ÖNEMLİ: Hikayeyi kesinlikle birinci tekil şahıs ('Ben') ağzından anlat, olay tamamen senin başından geçmiş gibi samimi bir dil kullan. "
        "ÇOK ÖNEMLİ: Okunduğunda maksimum 50 saniye sürmesi için metni yaklaşık 110-130 kelime uzunluğunda tut. Gereksiz detayları at, akışı hızlandır. "
        "ÇOK ÖNEMLİ: Hikayenin türünü ve havasını incele. Aşağıdaki listeden en uygun arka plan müziğini seç:\n"
        "- Sneaky Snitch (Gizem / Komedi, yalan söyleme, gizli işler)\n"
        "- Scheming Weasel Faster (Kaotik Komedi, kavga, absürt olaylar)\n"
        "- Monkeys Spinning Monkeys (Eğlenceli, utandırıcı anılar)\n"
        "- Fluffing a Duck (Hafif Komedi, günlük tatlı hikayeler)\n"
        "- Sneaky Adventure (Macera, keşif)\n"
        "- Investigations (Ciddi Gizem, suç, TIFU, paranormal)\n"
        "- Wii Music (Rahat, sakin)\n"
        "- Wii Shop Channel (Eğlenceli, nostaljik, bilgi/liste)\n"
        "Yanıtının EN BAŞINA şu formatta etiketleri koy: [GENDER: MALE veya FEMALE] [MUSIC: Seçtiğin Müzik Adı]. Örneğin: [GENDER: MALE] [MUSIC: Monkeys Spinning Monkeys]\n"
        "Hemen altına boşluk bırakıp sadece okunacak senaryoyu yaz. Başka açıklama yapma."
    )
    
    prompt = custom_prompt if custom_prompt else default_prompt
    full_content = f"BAŞLIK: {title}\n\nHİKAYE:\n{text}"
    
    try:
        result_text = ""
        if AI_PROVIDER == "gemini":
            response = gemini_model.generate_content([prompt, full_content])
            result_text = response.text.strip()
            
        elif AI_PROVIDER in ["openai", "deepseek"]:
            response = await openai_client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": full_content}
                ],
                temperature=0.7
            )
            result_text = response.choices[0].message.content.strip()
            
        else:
            raise ValueError(f"Unknown AI_PROVIDER: {AI_PROVIDER}")
        
        # Parse Gender Tag
        gender = "male" # default
        if "[GENDER: FEMALE]" in result_text.upper():
            gender = "female"
            
        # Parse Music Tag
        music = "Wii Music" # default
        music_match = re.search(r'\[MUSIC:(.*?)\]', result_text, flags=re.IGNORECASE)
        if music_match:
            music = music_match.group(1).strip()
            
        # Clean tags from the text
        result_text = re.sub(r'\[GENDER:.*?\]', '', result_text, flags=re.IGNORECASE).strip()
        result_text = re.sub(r'\[MUSIC:.*?\]', '', result_text, flags=re.IGNORECASE).strip()
            
        voice = "tr-TR-EmelNeural" if gender == "female" else "tr-TR-AhmetNeural"
        
        return {
            "text": result_text,
            "voice": voice,
            "gender": gender,
            "music": music
        }
            
    except Exception as e:
        print(f"[{AI_PROVIDER.upper()}] API Error: {e}")
        return None
