#!/usr/bin/env python3
"""Explore Galxe Quest platform (app.galxe.com)."""
import asyncio
from playwright.async_api import async_playwright

async def explore_galxe_quest():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Try app.galxe.com
        urls = [
            "https://app.galxe.com",
            "https://galxe.com/quest",
            "https://galxe.com/quests",
            "https://galxe.com/campaigns",
        ]
        
        for url in urls:
            print(f"\n=== Trying {url} ===")
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(5000)
                
                body_text = await page.inner_text('body')
                print(f"Content (first 3000): {body_text[:3000]}")
                
                # Look for quest cards
                quest_cards = await page.query_selector_all('[class*="quest"], [class*="campaign"], [class*="card"]')
                print(f"Quest cards: {len(quest_cards)}")
                for card in quest_cards[:10]:
                    text = await card.inner_text()
                    if text.strip() and len(text.strip()) > 20:
                        print(f"  Card: {text.strip()[:200]}")
                
            except Exception as e:
                print(f"Error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_galxe_quest())