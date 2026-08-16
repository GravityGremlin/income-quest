#!/usr/bin/env python3
"""
Quick debug script to see Hyper page after signup
"""
import asyncio
import sys
sys.path.insert(0, '/home/user/playwright-venv/lib/python3.11/site-packages')
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        # Go to Hyper auth page
        await page.goto("https://hyper.charm.land/auth?mode=signup", wait_until="domcontentloaded", timeout=30000)
        print(f"URL: {page.url}")
        print(f"Title: {await page.title()}")
        
        # Get page content
        content = await page.content()
        with open("/home/user/income-quest/hyper_page.html", "w") as f:
            f.write(content)
        print(f"Page content saved to hyper_page.html ({len(content)} chars)")
        print(f"First 3000 chars:\n{content[:3000]}")
        
        await page.screenshot(path="/home/user/income-quest/hyper_debug.png", full_page=True)
        await browser.close()

asyncio.run(main())