#!/usr/bin/env python3
"""Explore Layer3 discover page."""
import asyncio
import httpx
from bs4 import BeautifulSoup
import json

async def explore_layer3_discover():
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
        urls = [
            "https://layer3.xyz/discover",
            "https://layer3.xyz/discover?tab=streaks",
        ]
        
        for url in urls:
            print(f"\n🔍 Navigating to {url}...")
            try:
                resp = await client.get(url)
                print(f"Status: {resp.status_code}")
                print(f"Final URL: {resp.url}")
                
                with open(f"/home/user/income-quest/layer3_{url.replace('/', '_').replace('?', '_').replace('=', '_')}.html", "w") as f:
                    f.write(resp.text)
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                title = soup.find('title')
                print(f"Title: {title.text if title else 'N/A'}")
                
                body_text = soup.get_text()[:5000]
                print(f"Text preview: {body_text[:1000]}...")
                
                # Find all links
                all_links = soup.find_all('a', href=True)
                print(f"Total links: {len(all_links)}")
                
                quest_links = []
                for link in all_links[:200]:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    if text and any(kw in text.lower() for kw in ['quest', 'campaign', 'earn', 'reward', 'task', 'learn', 'cube', 'streak', 'bounty', 'daily', 'usdc', 'points', 'mint', 'activation', 'cube']):
                        quest_links.append((href, text[:100]))
                
                print(f"Quest-related links: {len(quest_links)}")
                for href, text in quest_links[:20]:
                    print(f"  {href} - {text}")
                    
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(explore_layer3_discover())