#!/usr/bin/env python3
"""
Verify Stacker News account is fully set up and explore earning options.
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
        await page.goto("https://stacker.news/", wait_until="networkidle")
        
        # Check if logged in - look for user menu, wallet, etc.
        content = await page.content()
        
        # Save page for inspection
        with open('/home/user/income-quest/data/stacker_home.html', 'w') as f:
            f.write(content)
        
        # Look for indicators of logged-in state
        indicators = [
            'wallet', 'balance', 'sats', 'lightning', 'zap', 
            'profile', 'logout', 'username', 'sign out'
        ]
        
        print("=== Page Analysis ===")
        for indicator in indicators:
            if indicator.lower() in content.lower():
                print(f"Found '{indicator}' in page")
        
        # Check for user menu / profile link
        user_elements = await page.query_selector_all('a[href*="profile"], a[href*="user"], a[href*="me"], .user-menu, [data-testid*="user"]')
        print(f"\nUser/profile elements found: {len(user_elements)}")
        for el in user_elements:
            text = await el.text_content()
            href = await el.get_attribute('href')
            print(f"  - text: '{text}', href: '{href}'")
        
        # Check for wallet/balance display
        wallet_elements = await page.query_selector_all('[class*="wallet"], [class*="balance"], [class*="sats"]')
        print(f"\nWallet/balance elements: {len(wallet_elements)}")
        for el in wallet_elements:
            text = await el.text_content()
            cls = await el.get_attribute('class')
            print(f"  - class: '{cls}', text: '{text[:100]}'")
        
        # Try to navigate to profile page
        print("\n--- Trying profile page ---")
        profile_page = await context.new_page()
        await profile_page.goto("https://stacker.news/me", wait_until="networkidle")
        profile_content = await profile_page.content()
        with open('/home/user/income-quest/data/stacker_profile.html', 'w') as f:
            f.write(profile_content)
        
        # Check if profile page shows user info
        if 'username' in profile_content.lower() or 'profile' in profile_content.lower():
            print("Profile page accessible!")
        else:
            print("Profile page may require login completion")
            # Look for signup completion forms
            inputs = await profile_page.query_selector_all('input')
            print(f"Inputs on profile page: {len(inputs)}")
            for inp in inputs:
                attrs = await inp.evaluate('el => ({name: el.name, type: el.type, placeholder: el.placeholder, id: el.id})')
                print(f"  {attrs}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())