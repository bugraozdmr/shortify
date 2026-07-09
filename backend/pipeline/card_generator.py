import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from loguru import logger

def get_font(size: int) -> ImageFont.FreeTypeFont:
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception as e:
                logger.error(f"Error loading font {p}: {e}")
                continue
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        logger.error("Could not load any custom font, using default (text will be small!)")
        return ImageFont.load_default()

def draw_rounded_rectangle(draw, bounds, radius, fill):
    """PIL kullanarak köşeleri yuvarlatılmış dikdörtgen çizer."""
    x0, y0, x1, y1 = bounds
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.pieslice([x0, y0, x0 + radius * 2, y0 + radius * 2], 180, 270, fill=fill)
    draw.pieslice([x1 - radius * 2, y0, x1, y0 + radius * 2], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - radius * 2, x0 + radius * 2, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - radius * 2, y1 - radius * 2, x1, y1], 0, 90, fill=fill)

def generate_social_card(logo_path: str, channel_name: str, title_text: str, output_path: str):
    logger.info("Generating social media card...")
    
    # Boyut ayarları
    card_width = 650
    padding = 40
    logo_size = 90
    
    # Fontları Yükle (Türkçe karakter desteği garanti olan Arial Bold)
    font_name = get_font(32)
    font_text = get_font(36) # Daha kalın ve okunaklı

    
    # Metni sarma (text wrap)
    wrapped_lines = textwrap.wrap(title_text, width=32)
    
    # Yüksekliği metne göre hesapla
    # logo alanı (padding + logo_size + padding/2) + her satır için yükseklik + padding
    line_height = 45
    text_height = len(wrapped_lines) * line_height
    card_height = padding + logo_size + (padding//2) + text_height + padding
    
    # Şeffaf arka planlı ana görsel oluştur
    img = Image.new('RGBA', (card_width, card_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Siyah hafif gölge (isteğe bağlı, daha derinlik katar)
    shadow_offset = 6
    draw_rounded_rectangle(draw, (shadow_offset, shadow_offset, card_width, card_height), 30, (0, 0, 0, 80))
    
    # Beyaz kartı çiz (köşeleri yuvarlatılmış)
    draw_rounded_rectangle(draw, (0, 0, card_width-shadow_offset, card_height-shadow_offset), 30, (255, 255, 255, 255))
    
    # Logoyu yükle ve çiz
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # Logoyu yuvarlak yapmak için maske (Opsiyonel, eğer logo kare ise)
        mask = Image.new('L', (logo_size, logo_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, logo_size, logo_size), fill=255)
        
        # Beyaz arka plana paste et
        img.paste(logo, (padding, padding), mask)
    else:
        logger.warning(f"Logo not found at {logo_path}, skipping logo drawing.")
    
    # Kanal ismini yaz
    text_x = padding + logo_size + 20
    text_y = padding + (logo_size // 2) - 16
    draw.text((text_x, text_y), channel_name, font=font_name, fill=(0, 0, 0, 255))
    
    # Mavi Doğrulama Tiki (Mavi daire + beyaz onay işareti)
    try:
        # Metnin genişliğini hesaplayıp mavi tiki yanına koyalım
        bbox = draw.textbbox((text_x, text_y), channel_name, font=font_name)
        name_width = bbox[2] - bbox[0]
        tick_x = text_x + name_width + 10
        tick_y = text_y + 8
        draw.ellipse((tick_x, tick_y, tick_x+22, tick_y+22), fill="#1DA1F2")
        # Beyaz onay işareti (V) çiz
        draw.line([(tick_x + 6, tick_y + 11), (tick_x + 10, tick_y + 15), (tick_x + 16, tick_y + 7)], fill="white", width=3)
    except:
        pass # bbox fails on older PIL, ignore tick
    
    # Başlık Metnini (Title Text) yazdır
    current_y = padding + logo_size + (padding // 2)
    for line in wrapped_lines:
        draw.text((padding, current_y), line, font=font_text, fill=(20, 20, 20, 255))
        current_y += line_height
        
    img.save(output_path)
    logger.info(f"Social card generated at {output_path}")
    return output_path
