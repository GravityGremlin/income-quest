#!/usr/bin/env python3
"""
Try to create a new post on Stacker News - may trigger username setup.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Load cookies
        with open('/home/user/income-quest/data/stacker_news_cookies.json', 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        # Try the new post page
        await page.goto("https://stacker.news/~/new", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        content = await page.content()
        with open('/home/user/income-quest/data/stacker_new_post.html', 'w') as f:
            f.write(content)
        
        print(f"URL: {page.url}")
        text = await page.text_content('body')
        print("=== NEW POST PAGE ===")
        print(text[:3000])
        
        # Look for title/content inputs
        inputs = await page.query_selector_all('input, textarea')
        print(f"\nInputs found: {len(inputs)}")
        for inp in inputs:
            attrs = await inp.evaluate('el => ({name: el.name, type: el.type, placeholder: el.placeholder, id: el.id, tag: el.tagName})')
            print(f"  {attrs}")
        
        # If redirected to signup, we need to complete profile
        if 'signup' in page.url or 'signin' in page.url:
            print("\nRedirected to auth - need to complete profile setup")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())