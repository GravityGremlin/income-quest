#!/usr/bin/env python3
"""Explore a specific Galxe quest space."""
import asyncio
import httpx
from bs4 import BeautifulSoup
import json

async def explore_galxe_space():
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
        # Check a specific space with daily quests - Lumio Daily Routine
        print("🔍 Checking Lumio Daily Routine space...")
        resp = await client.get("https://app.galxe.com/quest/lumio")
        print(f"Space page status: {resp.status_code}")
        print(f"Final URL: {resp.url}")
        
        with open("/home/user/income-quest/galxe_lumio.html", "w") as f:
            f.write(resp.text)
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        body_text = soup.get_text()[:8000]
        print(f"Space page text (first 8000): {body_text}")
        
        # Look for wallet connect
        buttons = soup.find_all('button')
        for btn in buttons:
            text = btn.get_text(strip=True)
            if text and any(kw in text.lower() for kw in ['connect', 'wallet', 'login', 'metamask', 'walletconnect', 'rainbow', 'coinbase', 'ledger', 'verify', 'claim', 'participate']):
                print(f"Action button: {text[:200]}")
                print(f"  HTML: {str(btn)[:500]}")

        # Check for quest details
        all_text = soup.get_text()
        if 'daily' in all_text.lower() or 'point' in all_text.lower():
            print("\n=== QUEST DETAILS FOUND ===")
            # Print more context around daily/point mentions
            for line in all_text.split('\n'):
                if 'daily' in line.lower() or 'point' in line.lower() or 'reward' in line.lower():
                    print(f"  {line.strip()[:200]}")

if __name__ == "__main__":
    asyncio.run(explore_galxe_space())