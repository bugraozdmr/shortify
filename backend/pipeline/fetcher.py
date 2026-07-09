import asyncio
from playwright.async_api import async_playwright
from loguru import logger
from utils.constants import USER_AGENTS

import random

async def fetch_best_posts(subreddit_name: str = "tifu", limit: int = 5):
    posts = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS)
        )
        page = await context.new_page()
        
        logger.info(f"Fetching posts from r/{subreddit_name}...")
        
        await page.goto(f"https://old.reddit.com/r/{subreddit_name}/top/?sort=top&t=day")
        
        post_elements = await page.query_selector_all(".thing")
        
        post_urls = []
        for el in post_elements[:limit]:
            permalink = await el.get_attribute("data-permalink")
            reddit_id = await el.get_attribute("data-fullname")
            
            classes = await el.get_attribute("class")
            if permalink and "stickied" not in classes:
                post_urls.append({"id": reddit_id, "url": f"https://old.reddit.com{permalink}"})
        
        for item in post_urls:
            await page.goto(item["url"])
            
            title_el = await page.query_selector("a.title")
            title = await title_el.inner_text() if title_el else "Unknown Title"
            
            body_el = await page.query_selector(".entry .usertext-body .md")
            text = await body_el.inner_text() if body_el else ""
            
            if text:
                posts.append({
                    "reddit_id": item["id"],
                    "title": title,
                    "text": text
                })
                logger.info(f"Fetched: {title}")
        
        await browser.close()
        
    return posts

