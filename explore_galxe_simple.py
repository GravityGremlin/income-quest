#!/usr/bin/env python3
"""Explore Galxe.com for crypto quests using HTTP only with proper encoding handling."""
import asyncio
import httpx
from bs4 import BeautifulSoup
import json
import gzip
import brotli

async def explore_galxe():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',  # Remove br to avoid brotli issues
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
        print("🔍 Navigating to Galxe.com...")
        resp = await client.get("https://galxe.com")
        print(f"Status: {resp.status_code}")
        print(f"Final URL: {resp.url}")
        print(f"Content-Encoding: {resp.headers.get('content-encoding', 'none')}")
        
        # httpx handles decompression automatically
        html = resp.text
        
        # Save HTML for analysis
        with open("/home/user/income-quest/galxe_home_simple.html", "w") as f:
            f.write(html)
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Get page title
        title = soup.find('title')
        print(f"Title: {title.text if title else 'N/A'}")
        
        # Look for quest-related content
        body_text = soup.get_text()[:5000]
        print(f"\n=== BODY TEXT (first 5000) ===")
        print(body_text)
        
        # Find all links
        all_links = soup.find_all('a', href=True)
        print(f"\nTotal links: {len(all_links)}")
        
        quest_links = []
        for link in all_links[:200]:
            href = link.get('href')
            text = link.get_text(strip=True)
            if text and any(kw in text.lower() for kw in ['quest', 'campaign', 'earn', 'reward', 'task', 'bounty', 'airdrop', 'points', 'xp']):
                quest_links.append((href, text[:100]))
        
        print(f"Quest-related links: {len(quest_links)}")
        for href, text in quest_links[:30]:
            print(f"  {href} - {text}")
        
        # Check for wallet connect buttons
        buttons = soup.find_all('button')
        wallet_btns = [b for b in buttons if any(kw in b.get_text(strip=True).lower() for kw in ['connect', 'wallet', 'login', 'sign in', 'join'])]
        print(f"\nWallet/connect buttons: {len(wallet_btns)}")
        for btn in wallet_btns[:10]:
            print(f"  {btn.get_text(strip=True)[:100]}")
        
        # Look for script tags with config/data
        scripts = soup.find_all('script', type='application/json')
        for script in scripts[:5]:
            try:
                data = json.loads(script.string)
                print(f"\nFound JSON config: {json.dumps(data)[:500]}...")
            except:
                pass
        
        # Check for next.js / app router data
        next_data = soup.find('script', id='__NEXT_DATA__')
        if next_data:
            print("\n=== FOUND __NEXT_DATA__ ===")
            try:
                data = json.loads(next_data.string)
                # Save for deeper analysis
                with open("/home/user/income-quest/galxe_next_data.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("Saved to galxe_next_data.json")
            except Exception as e:
                print(f"Failed to parse: {e}")

if __name__ == "__main__":
    asyncio.run(explore_galxe())