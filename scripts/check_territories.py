#!/usr/bin/env python3
"""
Search Stacker News for SatsBoard territory.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        page = await context.new_page()
        await page.goto("https://stacker.news/territories", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        content = await page.content()
        with open('/home/user/income-quest/data/stacker_territories.html', 'w') as f:
            f.write(content)
        
        text = await page.text_content('body')
        print("=== TERRITORIES PAGE ===")
        print(text[:5000])
        
        # Search for satsboard
        import re
        if 'satsboard' in text.lower() or 'sats board' in text.lower():
            print("\nFound SatsBoard reference!")
        else:
            print("\nNo SatsBoard found in territories")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())