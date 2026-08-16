#!/usr/bin/env python3
"""
Set username on Stacker News and explore earning sats.
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
        
        # Try to access settings/profile edit page
        await page.goto("https://stacker.news/settings", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        content = await page.content()
        with open('/home/user/income-quest/data/stacker_settings.html', 'w') as f:
            f.write(content)
        
        print(f"Settings URL: {page.url}")
        
        # Look for username field
        text = await page.text_content('body')
        print("=== SETTINGS PAGE TEXT (first 3000) ===")
        print(text[:3000])
        
        # Check for username input
        username_inputs = await page.query_selector_all('input[name="username"], input[name="name"], input[placeholder*="username" i], input[id*="username" i]')
        print(f"\nUsername inputs found: {len(username_inputs)}")
        for inp in username_inputs:
            attrs = await inp.evaluate('el => ({name: el.name, type: el.type, placeholder: el.placeholder, id: el.id, value: el.value})')
            print(f"  {attrs}")
        
        # If username is @wallet (default), try to change it
        if '@wallet' in text:
            print("\n--- Attempting to set custom username ---")
            if username_inputs:
                username = f"agent_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
                await username_inputs[0].fill(username)
                print(f"Filled username: {username}")
                
                # Find save button
                save_btns = await page.query_selector_all('button[type="submit"], button:has-text("Save"), button:has-text("Update")')
                for btn in save_btns:
                    btn_text = await btn.text_content()
                    print(f"  Found button: {btn_text}")
                    if 'save' in btn_text.lower() or 'update' in btn_text.lower() or btn.get_attribute('type') == 'submit':
                        await btn.click()
                        await page.wait_for_timeout(3000)
                        print("Clicked save")
                        break
                
                # Verify
                new_content = await page.content()
                if username in new_content:
                    print(f"SUCCESS: Username changed to {username}")
                else:
                    print("Username change may not have worked")
            else:
                print("No username input found on settings page")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())