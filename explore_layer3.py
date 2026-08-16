#!/usr/bin/env python3
"""Explore Layer3.xyz for crypto quests/tasks."""
import asyncio
from playwright.async_api import async_playwright

async def explore_layer3():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        print("🔍 Navigating to Layer3.xyz...")
        await page.goto("https://layer3.xyz", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        await page.screenshot(path="/home/user/income-quest/layer3_home.png", full_page=True)
        
        body_text = await page.inner_text('body')
        print(f"=== BODY TEXT (first 5000) ===")
        print(body_text[:5000])
        
        # Look for quest/task related content
        all_links = await page.query_selector_all('a[href]')
        print(f"\nTotal links: {len(all_links)}")
        for link in all_links[:50]:
            href = await link.get_attribute('href')
            text = await link.inner_text()
            if text.strip():
                print(f"  {href} - {text.strip()[:100]}")
        
        # Check for connect wallet / sign in
        auth_buttons = await page.query_selector_all('button:has-text("Connect"), button:has-text("Sign in"), button:has-text("Login"), a:has-text("Connect"), a:has-text("Sign in")')
        for btn in auth_buttons:
            text = await btn.inner_text()
            print(f"Auth button: {text.strip()}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_layer3())