import asyncio
from playwright.async_api import async_playwright
from loguru import logger
from utils.constants import USER_AGENTS

import random

async def fetch_best_posts(subreddit_name: str = "tifu", limit: int = 5, existing_ids: set = None, max_pages: int = 5):
    if existing_ids is None:
        existing_ids = set()
        
    posts = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS)
        )
        page = await context.new_page()
        
        logger.info(f"Fetching posts from r/{subreddit_name}...")
        
        current_url = f"https://old.reddit.com/r/{subreddit_name}/"
        post_urls = []
        
        for page_num in range(max_pages): # Dynamic limit
            await page.goto(current_url)
            
            post_elements = await page.query_selector_all(".thing")
            for el in post_elements:
                classes = await el.get_attribute("class") or ""
                is_promoted = await el.get_attribute("data-promoted")
                
                if "stickied" in classes or "promoted" in classes or is_promoted == "true":
                    continue
                    
                permalink = await el.get_attribute("data-permalink")
                reddit_id = await el.get_attribute("data-fullname")
                
                if not permalink or reddit_id in existing_ids:
                    continue
                    
                title_el = await el.query_selector("p.title a.title")
                title = await title_el.inner_text() if title_el else "Unknown Title"
                
                post_urls.append({
                    "id": reddit_id, 
                    "url": f"https://old.reddit.com{permalink}",
                    "title": title
                })
                
                if len(post_urls) >= limit:
                    break
                    
            if len(post_urls) >= limit:
                break
                
            # Find next page button
            next_button = await page.query_selector(".next-button a")
            if next_button:
                current_url = await next_button.get_attribute("href")
            else:
                break # No more pages
        
        for item in post_urls:
            await page.goto(item["url"])
            
            body_el = await page.query_selector(".entry .usertext-body .md")
            text = await body_el.inner_text() if body_el else ""
            
            if text:
                posts.append({
                    "reddit_id": item["id"],
                    "title": item["title"],
                    "text": text
                })
                logger.info(f"Fetched new post: {item['title']}")
        
        await browser.close()
        
    return posts

