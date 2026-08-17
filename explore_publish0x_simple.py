#!/usr/bin/env python3
"""Explore Publish0x for crypto blogging/reading rewards."""
import asyncio
import httpx
from bs4 import BeautifulSoup
import json

async def explore_publish0x():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
        print("🔍 Navigating to Publish0x.com...")
        resp = await client.get("https://www.publish0x.com")
        print(f"Status: {resp.status_code}")
        print(f"Final URL: {resp.url}")
        
        with open("/home/user/income-quest/publish0x_home.html", "w") as f:
            f.write(resp.text)
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        title = soup.find('title')
        print(f"Title: {title.text if title else 'N/A'}")
        
        body_text = soup.get_text()[:5000]
        print(f"\n=== BODY TEXT (first 5000) ===")
        print(body_text)
        
        # Find all links
        all_links = soup.find_all('a', href=True)
        print(f"\nTotal links: {len(all_links)}")
        
        earn_links = []
        for link in all_links[:200]:
            href = link.get('href')
            text = link.get_text(strip=True)
            if text and any(kw in text.lower() for kw in ['earn', 'reward', 'tip', 'crypto', 'write', 'read', 'publish', 'author', 'signup', 'register', 'login']):
                earn_links.append((href, text[:100]))
        
        print(f"Earn-related links: {len(earn_links)}")
        for href, text in earn_links[:30]:
            print(f"  {href} - {text}")
        
        # Check for next.js data
        next_data = soup.find('script', id='__NEXT_DATA__')
        if next_data:
            print("\n=== FOUND __NEXT_DATA__ ===")
            try:
                data = json.loads(next_data.string)
                with open("/home/user/income-quest/publish0x_next_data.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("Saved to publish0x_next_data.json")
            except Exception as e:
                print(f"Failed to parse: {e}")

if __name__ == "__main__":
    asyncio.run(explore_publish0x())