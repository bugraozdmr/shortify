import httpx
import asyncio
from bs4 import BeautifulSoup

async def main():
    url = "https://old.reddit.com/r/tifu/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        print("Status:", r.status_code)
        
        soup = BeautifulSoup(r.text, 'html.parser')
        things = soup.select('.thing')
        print("Things count:", len(things))
        
        if things:
            print("First thing title:", things[0].select_one('p.title a.title').text)

if __name__ == "__main__":
    asyncio.run(main())
