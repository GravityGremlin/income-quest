#!/usr/bin/env python3
"""Explore Galxe.com for crypto quests."""
import asyncio
from playwright.async_api import async_playwright

async def explore_galxe():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        print("🔍 Navigating to Galxe.com...")
        await page.goto("https://galxe.com", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        await page.screenshot(path="/home/user/income-quest/galxe_home.png", full_page=True)
        
        body_text = await page.inner_text('body')
        print(f"=== BODY TEXT (first 5000) ===")
        print(body_text[:5000])
        
        # Look for quest/campaign links
        all_links = await page.query_selector_all('a[href]')
        print(f"\nTotal links: {len(all_links)}")
        quest_links = []
        for link in all_links[:100]:
            href = await link.get_attribute('href')
            text = await link.inner_text()
            if text.strip() and ('quest' in text.lower() or 'campaign' in text.lower() or 'earn' in text.lower() or 'reward' in text.lower() or 'task' in text.lower()):
                quest_links.append((href, text.strip()[:100]))
        
        print(f"Quest-related links: {len(quest_links)}")
        for href, text in quest_links[:20]:
            print(f"  {href} - {text}")
        
        # Check for connect wallet
        wallet_btns = await page.query_selector_all('button:has-text("Connect"), button:has-text("Wallet"), button:has-text("Login"), button:has-text("Sign in")')
        for btn in wallet_btns:
            text = await btn.inner_text()
            print(f"Wallet button: {text.strip()}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_galxe())