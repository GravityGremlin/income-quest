#!/usr/bin/env python3
"""Explore Publish0x.com - crypto blogging platform."""
import asyncio
from playwright.async_api import async_playwright

async def explore_publish0x():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        print("🔍 Navigating to Publish0x.com...")
        await page.goto("https://www.publish0x.com", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        await page.screenshot(path="/home/user/income-quest/publish0x_home.png", full_page=True)
        
        body_text = await page.inner_text('body')
        print(f"=== BODY TEXT (first 5000) ===")
        print(body_text[:5000])
        
        # Look for signup/earn
        all_links = await page.query_selector_all('a[href]')
        earn_links = []
        for link in all_links[:100]:
            href = await link.get_attribute('href')
            text = await link.inner_text()
            if text.strip() and ('earn' in text.lower() or 'signup' in text.lower() or 'register' in text.lower() or 'join' in text.lower() or 'reward' in text.lower() or 'tip' in text.lower()):
                earn_links.append((href, text.strip()[:100]))
        
        print(f"Earn/signup links: {len(earn_links)}")
        for href, text in earn_links[:20]:
            print(f"  {href} - {text}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_publish0x())