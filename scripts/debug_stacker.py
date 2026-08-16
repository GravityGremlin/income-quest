#!/usr/bin/env python3
"""
Debug Stacker News signup page structure - write to file.
"""
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://stacker.news/signup", wait_until="networkidle")
        
        # Print page content for debugging
        content = await page.content()
        with open('/home/user/income-quest/data/stacker_signup_page.html', 'w') as f:
            f.write(content)
        
        # Try to find all input elements
        inputs = await page.query_selector_all('input')
        with open('/home/user/income-quest/data/stacker_debug.txt', 'w') as f:
            f.write(f"Found {len(inputs)} input elements:\n")
            for i, inp in enumerate(inputs):
                attrs = await inp.evaluate('el => ({type: el.type, name: el.name, id: el.id, placeholder: el.placeholder, class: el.className})')
                f.write(f"  {i}: {attrs}\n")
            
            # Try to find all buttons
            buttons = await page.query_selector_all('button')
            f.write(f"\nFound {len(buttons)} button elements:\n")
            for i, btn in enumerate(buttons):
                text = await btn.text_content()
                attrs = await btn.evaluate('el => ({type: el.type, class: el.className})')
                f.write(f"  {i}: text='{text}', attrs={attrs}\n")
        
        await browser.close()
        print("Debug info written to files")


if __name__ == "__main__":
    asyncio.run(main())