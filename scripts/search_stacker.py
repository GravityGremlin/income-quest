#!/usr/bin/env python3
"""
Search Stacker News for SatsBoard or similar task platforms.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        page = await context.new_page()
        await page.goto("https://stacker.news/search?q=SatsBoard", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        content = await page.content()
        with open('/home/user/income-quest/data/stacker_search_satsboard.html', 'w') as f:
            f.write(content)
        
        text = await page.text_content('body')
        print("=== SEARCH RESULTS ===")
        print(text[:5000])
        
        # Also search for "task", "bounty", "earn"
        for query in ["task", "bounty", "earn sats", "microtask", "freelance"]:
            print(f"\n--- Searching for '{query}' ---")
            q_page = await context.new_page()
            await q_page.goto(f"https://stacker.news/search?q={query}", wait_until="networkidle")
            await q_page.wait_for_timeout(2000)
            q_text = await q_page.text_content('body')
            print(q_text[:2000])
            await q_page.close()
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())