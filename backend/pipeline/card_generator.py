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
    import random
    logger.info("Generating social media card...")
    
    # Boyut ayarları
    card_width = 650
    padding = 40
    logo_size = 90
    
    # Fontları Yükle
    font_name = get_font(32)
    font_text = get_font(36)
    font_small = get_font(24)
    
    # Emojileri temizle
    import re
    title_text = re.sub(r'[^\w\s.,!?"\'\-:;()@#$%^&*+=<>/\\~\[\]{}“”‘’–—]', '', title_text)
    
    # Metni sarma (text wrap) - 24 karaktere düşürdük taşmayı engellemek için
    wrapped_lines = textwrap.wrap(title_text, width=24)
    
    # Yüksekliği metne göre hesapla
    line_height = 45
    text_height = len(wrapped_lines) * line_height
    action_bar_height = 50
    
    # logo alanı (padding + logo_size + padding/2) + her satır için yükseklik + action bar + padding
    card_height = padding + logo_size + (padding//2) + text_height + action_bar_height + padding
    
    # Şeffaf arka planlı ana görsel oluştur
    img = Image.new('RGBA', (card_width, card_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Siyah hafif gölge
    shadow_offset = 8
    draw_rounded_rectangle(draw, (shadow_offset, shadow_offset, card_width, card_height), 30, (0, 0, 0, 70))
    
    # Beyaz kartı çiz (köşeleri yuvarlatılmış)
    draw_rounded_rectangle(draw, (0, 0, card_width-shadow_offset, card_height-shadow_offset), 30, (255, 255, 255, 255))
    
    # Logoyu yükle ve çiz
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            mask = Image.new('L', (logo_size, logo_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, logo_size, logo_size), fill=255)
            img.paste(logo, (padding, padding), mask)
        except Exception as e:
            logger.error(f"Logo error: {e}")
            draw.ellipse([padding, padding, padding+logo_size, padding+logo_size], fill="#FF4500")
    else:
        logger.warning(f"Logo not found at {logo_path}, skipping logo drawing.")
        draw.ellipse([padding, padding, padding+logo_size, padding+logo_size], fill="#FF4500")
    
    # Kanal ismini yaz
    text_x = padding + logo_size + 20
    text_y = padding + (logo_size // 2) - 16
    draw.text((text_x, text_y), channel_name, font=font_name, fill=(0, 0, 0, 255))
    
    # Mavi Doğrulama Tiki
    try:
        bbox = draw.textbbox((text_x, text_y), channel_name, font=font_name)
        name_width = bbox[2] - bbox[0]
        tick_x = text_x + name_width + 10
        tick_y = text_y + 8
        draw.ellipse((tick_x, tick_y, tick_x+22, tick_y+22), fill="#1DA1F2")
        draw.line([(tick_x + 6, tick_y + 11), (tick_x + 10, tick_y + 15), (tick_x + 16, tick_y + 7)], fill="white", width=3)
    except:
        pass
    
    # Başlık Metnini (Title Text) yazdır
    current_y = padding + logo_size + (padding // 2)
    for line in wrapped_lines:
        draw.text((padding, current_y), line, font=font_text, fill=(20, 20, 20, 255))
        current_y += line_height
        
    # Action Bar (Beğen, Yorum vs)
    action_y = current_y + 10
    icon_color = (135, 138, 140, 255)
    
    # Kalp / Upvote (arrow up)
    up_pts = [
        (padding + 10, action_y + 12),
        (padding + 16, action_y + 2),
        (padding + 22, action_y + 12),
        (padding + 18, action_y + 12),
        (padding + 18, action_y + 22),
        (padding + 14, action_y + 22),
        (padding + 14, action_y + 12)
    ]
    draw.polygon(up_pts, fill=icon_color)
    
    # Likes Count
    likes = f"{random.randint(10, 99)}.{random.randint(1, 9)}k"
    draw.text((padding + 35, action_y), likes, font=font_small, fill=icon_color)
    
    # Downvote Icon (arrow down)
    down_x_offset = padding + 120
    down_pts = [
        (down_x_offset + 10, action_y + 12),
        (down_x_offset + 14, action_y + 12),
        (down_x_offset + 14, action_y + 2),
        (down_x_offset + 18, action_y + 2),
        (down_x_offset + 18, action_y + 12),
        (down_x_offset + 22, action_y + 12),
        (down_x_offset + 16, action_y + 22)
    ]
    draw.polygon(down_pts, fill=icon_color)
    
    # Comment Icon (chat bubble)
    chat_x = down_x_offset + 50
    draw_rounded_rectangle(draw, (chat_x, action_y + 4, chat_x + 24, action_y + 20), 4, icon_color)
    draw.polygon([(chat_x + 4, action_y + 20), (chat_x + 12, action_y + 20), (chat_x + 4, action_y + 28)], fill=icon_color)
    
    # Comment Count
    comments = str(random.randint(200, 1500))
    draw.text((chat_x + 35, action_y), comments, font=font_small, fill=icon_color)
    
    img.save(output_path)
    logger.info(f"Social card generated at {output_path}")
    return output_path

def generate_comment_card(author: str, text: str, output_path: str):
    import random
    import re
    logger.info(f"Generating comment card for {author}...")
    
    # Emojileri ve desteklenmeyen karakterleri temizle (sadece harf, rakam ve yaygın noktalama işaretlerini tut)
    text = re.sub(r'[^\w\s.,!?"\'\-:;()@#$%^&*+=<>/\\~\[\]{}“”‘’–—]', '', text)
    author = re.sub(r'[^\w\s.\-_]', '', author)
    
    card_width = 600
    padding = 25
    
    font_name = get_font(24)
    font_text = get_font(28)
    font_small = get_font(22)
    
    wrapped_lines = textwrap.wrap(text, width=38)
    line_height = 35
    text_height = len(wrapped_lines) * line_height
    
    avatar_size = 48
    action_bar_height = 40
    
    # Author name height + spacing + text height + action bar + paddings
    card_height = padding + avatar_size + 15 + text_height + 15 + action_bar_height + padding
    
    img = Image.new('RGBA', (card_width, card_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    shadow_offset = 6
    draw_rounded_rectangle(draw, (shadow_offset, shadow_offset, card_width, card_height), 20, (0, 0, 0, 80))
    draw_rounded_rectangle(draw, (0, 0, card_width-shadow_offset, card_height-shadow_offset), 20, (255, 255, 255, 255))
    
    # Draw avatar
    avatar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "images", "reddit.jpeg")
    if os.path.exists(avatar_path):
        try:
            avatar = Image.open(avatar_path).convert("RGBA")
            avatar = avatar.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
            
            # Mask to make it circular
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            img.paste(avatar, (padding, padding), mask)
        except Exception as e:
            logger.error(f"Failed to draw avatar: {e}")
            draw.ellipse([padding, padding, padding+avatar_size, padding+avatar_size], fill="#FF4500")
    else:
        # Fallback to orange circle
        draw.ellipse([padding, padding, padding+avatar_size, padding+avatar_size], fill="#FF4500")
    
    # Draw author name
    author_text = f"@{author}"
    # Center text vertically with avatar
    text_y = padding + (avatar_size // 2) - 12
    draw.text((padding + avatar_size + 15, text_y), author_text, font=font_name, fill=(100, 100, 100, 255))
    
    # Draw comment text
    current_y = padding + avatar_size + 15
    for line in wrapped_lines:
        draw.text((padding, current_y), line, font=font_text, fill=(20, 20, 20, 255))
        current_y += line_height
        
    # Draw Action Bar (Upvote, Downvote, Comments)
    action_y = current_y + 15
    icon_color = (135, 138, 140, 255)
    
    # Upvote Icon (arrow up)
    up_pts = [
        (padding + 10, action_y + 12),
        (padding + 16, action_y + 2),
        (padding + 22, action_y + 12),
        (padding + 18, action_y + 12),
        (padding + 18, action_y + 22),
        (padding + 14, action_y + 22),
        (padding + 14, action_y + 12)
    ]
    draw.polygon(up_pts, fill=icon_color)
    
    # Upvote Count
    upvotes = f"{random.randint(1, 9)}.{random.randint(1, 9)}k"
    draw.text((padding + 32, action_y + 2), upvotes, font=font_small, fill=icon_color)
    
    # Downvote Icon (arrow down)
    down_x_offset = padding + 85
    down_pts = [
        (down_x_offset + 10, action_y + 12),
        (down_x_offset + 14, action_y + 12),
        (down_x_offset + 14, action_y + 2),
        (down_x_offset + 18, action_y + 2),
        (down_x_offset + 18, action_y + 12),
        (down_x_offset + 22, action_y + 12),
        (down_x_offset + 16, action_y + 22)
    ]
    draw.polygon(down_pts, fill=icon_color)
    
    # Comment Icon (chat bubble)
    chat_x = down_x_offset + 50
    draw_rounded_rectangle(draw, (chat_x, action_y + 4, chat_x + 20, action_y + 18), 4, icon_color)
    # Chat tail
    draw.polygon([(chat_x + 4, action_y + 18), (chat_x + 10, action_y + 18), (chat_x + 4, action_y + 24)], fill=icon_color)
    
    # Comment Count
    comments = str(random.randint(15, 300))
    draw.text((chat_x + 30, action_y + 2), comments, font=font_small, fill=icon_color)
    
    img.save(output_path)
    logger.info(f"Comment card generated at {output_path}")
    return output_path

def generate_outro_card(channel_name: str, output_path: str):
    logger.info("Generating outro card...")
    
    card_width = 500
    card_height = 340
    padding = 30
    
    font_title = get_font(42)
    font_sub = get_font(28)
    font_btn = get_font(30)
    
    img = Image.new('RGBA', (card_width, card_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    shadow_offset = 8
    draw_rounded_rectangle(draw, (shadow_offset, shadow_offset, card_width, card_height), 25, (0, 0, 0, 70))
    draw_rounded_rectangle(draw, (0, 0, card_width-shadow_offset, card_height-shadow_offset), 25, (255, 255, 255, 255))
    
    # Avatar (Centered)
    avatar_size = 100
    avatar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "images", "logo.png")
    
    avatar_x = (card_width - avatar_size) // 2
    avatar_y = padding
    
    if os.path.exists(avatar_path):
        try:
            avatar = Image.open(avatar_path).convert("RGBA")
            avatar = avatar.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            img.paste(avatar, (avatar_x, avatar_y), mask)
        except:
            draw.ellipse([avatar_x, avatar_y, avatar_x+avatar_size, avatar_y+avatar_size], fill="#1DA1F2")
    else:
        draw.ellipse([avatar_x, avatar_y, avatar_x+avatar_size, avatar_y+avatar_size], fill="#1DA1F2")
        
    # Channel Name (Centered)
    try:
        bbox = draw.textbbox((0, 0), channel_name, font=font_title)
        tw = bbox[2] - bbox[0]
    except:
        tw = 200
    draw.text(((card_width - tw) // 2, avatar_y + avatar_size + 15), channel_name, font=font_title, fill=(20, 20, 20, 255))
    
    # Mavi Doğrulama Tiki
    try:
        tick_x = ((card_width - tw) // 2) + tw + 10
        tick_y = avatar_y + avatar_size + 25
        draw.ellipse((tick_x, tick_y, tick_x+24, tick_y+24), fill="#1DA1F2")
        draw.line([(tick_x + 7, tick_y + 12), (tick_x + 11, tick_y + 16), (tick_x + 17, tick_y + 8)], fill="white", width=3)
    except:
        pass
        
    # Sub text (Centered)
    sub_text = "Daha fazlası için takip et!"
    try:
        bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
        stw = bbox[2] - bbox[0]
    except:
        stw = 250
    draw.text(((card_width - stw) // 2, avatar_y + avatar_size + 65), sub_text, font=font_sub, fill=(100, 100, 100, 255))
    
    # Subscribe button (Full width)
    btn_w = card_width - 60
    btn_h = 56
    btn_x = 30
    btn_y = card_height - btn_h - 30
    
    draw_rounded_rectangle(draw, (btn_x, btn_y, btn_x+btn_w, btn_y+btn_h), 28, (255, 0, 80, 255)) # TikTok/YouTube red/pink
    
    # Text in button
    btn_text = "Abone Ol"
    try:
        bbox = draw.textbbox((0, 0), btn_text, font=font_btn)
        btw = bbox[2] - bbox[0]
        bth = bbox[3] - bbox[1]
    except:
        btw = 100; bth = 20
        
    draw.text((btn_x + (btn_w - btw)//2, btn_y + (btn_h - bth)//2 - 2), btn_text, font=font_btn, fill=(255, 255, 255, 255))
    
    img.save(output_path)
    logger.info(f"Outro card generated at {output_path}")
    return output_path
