#!/usr/bin/env python3
"""Explore Galxe quests page and wallet connection."""
import asyncio
import httpx
from bs4 import BeautifulSoup
import json

async def explore_galxe_quests():
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
        # Check the quest page
        print("🔍 Checking quest page...")
        resp = await client.get("https://app.galxe.com/quest")
        print(f"Quest page status: {resp.status_code}")
        print(f"Final URL: {resp.url}")
        
        with open("/home/user/income-quest/galxe_quest.html", "w") as f:
            f.write(resp.text)
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        body_text = soup.get_text()[:8000]
        print(f"Quest page text (first 8000): {body_text}")
        
        # Look for daily quests
        all_links = soup.find_all('a', href=True)
        daily_quests = []
        for link in all_links:
            href = link.get('href')
            text = link.get_text(strip=True)
            if text and ('daily' in text.lower() or '25 points' in text.lower() or '20 points' in text.lower() or '15 points' in text.lower()):
                daily_quests.append((href, text[:200]))
        
        print(f"\nDaily quest links: {len(daily_quests)}")
        for href, text in daily_quests:
            print(f"  {href} - {text}")
        
        # Check for wallet connect
        buttons = soup.find_all('button')
        for btn in buttons:
            text = btn.get_text(strip=True)
            if text and any(kw in text.lower() for kw in ['connect', 'wallet', 'login', 'metamask', 'walletconnect', 'rainbow', 'coinbase', 'ledger']):
                print(f"Wallet button: {text[:200]}")
                print(f"  HTML: {str(btn)[:500]}")

        # Look for space URLs
        space_links = []
        for link in all_links:
            href = link.get('href')
            if href and '/quest/' in href and 'galxe.com' not in href:
                text = link.get_text(strip=True)
                space_links.append((href, text[:100]))
        
        print(f"\nQuest space links: {len(space_links)}")
        for href, text in space_links[:20]:
            print(f"  {href} - {text}")

if __name__ == "__main__":
    asyncio.run(explore_galxe_quests())