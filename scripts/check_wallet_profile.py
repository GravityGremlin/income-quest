#!/usr/bin/env python3
"""
Try to complete Stacker News profile setup by accessing the user profile page.
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
        
        # Try the user profile page - might be /~wallet or similar
        await page.goto("https://stacker.news/~wallet", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        content = await page.content()
        with open('/home/user/income-quest/data/stacker_wallet_profile.html', 'w') as f:
            f.write(content)
        
        print(f"URL: {page.url}")
        text = await page.text_content('body')
        print("=== PROFILE PAGE ===")
        print(text[:3000])
        
        # Look for edit profile button
        edit_links = await page.query_selector_all('a:has-text("edit"), a:has-text("Edit"), button:has-text("edit"), button:has-text("Edit")')
        print(f"\nEdit links/buttons: {len(edit_links)}")
        for el in edit_links:
            href = await el.get_attribute('href')
            text = await el.text_content()
            print(f"  href='{href}', text='{text}'")
        
        # Try to navigate to edit page if found
        if edit_links:
            href = await edit_links[0].get_attribute('href')
            if href:
                edit_page = await context.new_page()
                await edit_page.goto(f"https://stacker.news{href}" if href.startswith('/') else href, wait_until="networkidle")
                await edit_page.wait_for_timeout(2000)
                edit_content = await edit_page.content()
                with open('/home/user/income-quest/data/stacker_edit_profile.html', 'w') as f:
                    f.write(edit_content)
                edit_text = await edit_page.text_content('body')
                print("\n=== EDIT PROFILE PAGE ===")
                print(edit_text[:3000])
                
                # Look for username field
                username_inputs = await edit_page.query_selector_all('input[name="username"], input[name="name"], input[placeholder*="username" i]')
                print(f"\nUsername inputs: {len(username_inputs)}")
                for inp in username_inputs:
                    attrs = await inp.evaluate('el => ({name: el.name, value: el.value, placeholder: el.placeholder})')
                    print(f"  {attrs}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())