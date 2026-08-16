#!/usr/bin/env python3
"""Try to sign up for Layer3 and explore quests."""
import asyncio
from playwright.async_api import async_playwright

async def explore_layer3_quests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        print("🔍 Navigating to Layer3.xyz...")
        await page.goto("https://layer3.xyz", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        # Click "Get Started" or "Sign up"
        get_started = await page.query_selector('button:has-text("Get Started"), a:has-text("Get Started")')
        if get_started:
            await get_started.click()
            await page.wait_for_timeout(3000)
            print("Clicked Get Started")
        
        body_text = await page.inner_text('body')
        print(f"After Get Started: {body_text[:3000]}")
        
        # Check for wallet connection options
        wallet_btns = await page.query_selector_all('button:has-text("Wallet"), button:has-text("Connect"), button:has-text("Layer3 Wallet"), button:has-text("MetaMask"), button:has-text("Coinbase")')
        for btn in wallet_btns:
            text = await btn.inner_text()
            print(f"Wallet button: {text.strip()}")
        
        # Try to find "Activations" or "Quests" navigation
        nav_items = await page.query_selector_all('a:has-text("Activations"), a:has-text("Quests"), a:has-text("Earn"), a:has-text("Explore")')
        for item in nav_items:
            text = await item.inner_text()
            href = await item.get_attribute('href')
            print(f"Nav: {text.strip()} -> {href}")
            try:
                await item.click()
                await page.wait_for_timeout(3000)
                new_text = await page.inner_text('body')
                print(f"After click: {new_text[:3000]}")
            except Exception as e:
                print(f"Click failed: {e}")
        
        # Try direct URL for activations
        print("\n--- Trying direct activations URL ---")
        await page.goto("https://layer3.xyz/activations", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        body_text = await page.inner_text('body')
        print(f"Activations page: {body_text[:5000]}")
        
        # Look for quest cards
        quest_cards = await page.query_selector_all('[class*="quest"], [class*="activation"], [class*="task"], [class*="card"]')
        print(f"Quest cards found: {len(quest_cards)}")
        for card in quest_cards[:10]:
            text = await card.inner_text()
            if text.strip():
                print(f"  Card: {text.strip()[:200]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_layer3_quests())