#!/usr/usr/env python3
"""
Complete Stacker News signup - try to set username after magic code.
"""
import asyncio
import json
import random
import string
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
        
        # Try the email verification completion page
        await page.goto("https://stacker.news/email", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        content = await page.content()
        with open('/home/user/income-quest/data/stacker_email_page.html', 'w') as f:
            f.write(content)
        
        print(f"URL: {page.url}")
        text = await page.text_content('body')
        print("=== EMAIL PAGE ===")
        print(text[:3000])
        
        # Look for username input or next step
        inputs = await page.query_selector_all('input')
        print(f"\nInputs found: {len(inputs)}")
        for inp in inputs:
            attrs = await inp.evaluate('el => ({name: el.name, type: el.type, placeholder: el.placeholder, id: el.id, value: el.value})')
            print(f"  {attrs}")
        
        # If username input found, set it
        username_inputs = [inp for inp in inputs if 'username' in (await inp.get_attribute('name') or '').lower() or 'username' in (await inp.get_attribute('placeholder') or '').lower()]
        if username_inputs:
            username = f"agent_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
            await username_inputs[0].fill(username)
            print(f"Set username: {username}")
            
            # Find submit button
            submit_btn = await page.query_selector('button[type="submit"]')
            if submit_btn:
                await submit_btn.click()
                await page.wait_for_timeout(3000)
                print("Submitted username")
                print(f"New URL: {page.url}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())