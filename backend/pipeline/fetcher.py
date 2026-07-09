import asyncio
import httpx
from bs4 import BeautifulSoup
from loguru import logger
from utils.constants import USER_AGENTS

import random

async def fetch_best_posts(subreddit_name: str = "tifu", limit: int = 5, existing_ids: set = None, max_pages: int = 5):
    if existing_ids is None:
        existing_ids = set()
        
    posts = []
    
    logger.info(f"Fetching posts from r/{subreddit_name} (via httpx)...")
    
    current_url = f"https://old.reddit.com/r/{subreddit_name}/"
    post_urls = []
    
    headers = {
        "User-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
        
        current_url = f"https://old.reddit.com/r/{subreddit_name}/"
        post_urls = []
        
        for page_num in range(max_pages):
            r = None
            for attempt in range(3):
                headers["User-Agent"] = random.choice(USER_AGENTS)
                r = await client.get(current_url, headers=headers)
                if r.status_code == 200:
                    break
                logger.warning(f"Reddit deneme {attempt+1} başarısız: HTTP {r.status_code}")
                await asyncio.sleep(1)
                
            if not r or r.status_code != 200:
                logger.error(f"Reddit tamamen engelledi veya ulaşılamadı. Son status: {r.status_code if r else 'None'}")
                break
                
            soup = BeautifulSoup(r.text, 'html.parser')
            post_elements = soup.select(".thing")
            
            for el in post_elements:
                classes = el.get("class", [])
                is_promoted = el.get("data-promoted")
                
                if "stickied" in classes or "promoted" in classes or is_promoted == "true":
                    continue
                    
                permalink = el.get("data-permalink")
                reddit_id = el.get("data-fullname")
                
                if not permalink or reddit_id in existing_ids:
                    continue
                    
                title_el = el.select_one("p.title a.title")
                title = title_el.text if title_el else "Unknown Title"
                
                post_urls.append({
                    "id": reddit_id, 
                    "url": f"https://old.reddit.com{permalink}",
                    "title": title
                })
                
                if len(post_urls) >= limit:
                    break
                    
            if len(post_urls) >= limit:
                break
                
            next_button = soup.select_one(".next-button a")
            if next_button and next_button.get("href"):
                current_url = next_button.get("href")
            else:
                break
        
        for item in post_urls:
            r = None
            for attempt in range(3):
                headers["User-Agent"] = random.choice(USER_AGENTS)
                r = await client.get(item["url"], headers=headers)
                if r.status_code == 200:
                    break
                await asyncio.sleep(1)
                
            if r and r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                body_el = soup.select_one(".entry .usertext-body .md")
                text = body_el.text.strip() if body_el else ""
                
                if text:
                    posts.append({
                        "reddit_id": item["id"],
                        "title": item["title"],
                        "text": text
                    })
                    logger.info(f"Fetched new post: {item['title']}")
                    
    return posts

