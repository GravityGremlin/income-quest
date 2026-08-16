#!/usr/bin/env python3
"""
Check Stacker News account status and try to complete username setup if needed.
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
        await page.goto("https://stacker.news/~", wait_until="networkidle")  # User profile shortcut
        
        content = await page.content()
        with open('/home/user/income-quest/data/stacker_tilde.html', 'w') as f:
            f.write(content)
        
        current_url = page.url
        print(f"Current URL: {current_url}")
        
        # Check for username in page
        import re
        # Look for @username patterns
        usernames = re.findall(r'@([a-zA-Z0-9_]+)', content)
        print(f"Usernames found: {usernames[:20]}")
        
        # Check if we're on a user profile page (has username in URL or content)
        if '/~' in current_url and current_url != 'https://stacker.news/~':
            print(f"On user profile page: {current_url}")
        elif 'agent_' in content:
            print("Our agent username found in page!")
        else:
            print("May need to complete username setup")
            
            # Look for username input form
            inputs = await page.query_selector_all('input[name="username"], input[placeholder*="username" i], input[id*="username" i]')
            print(f"Username inputs found: {len(inputs)}")
            for inp in inputs:
                attrs = await inp.evaluate('el => ({name: el.name, type: el.type, placeholder: el.placeholder, id: el.id})')
                print(f"  {attrs}")
            
            # If username input found, set a username
            if inputs:
                username = f"agent_{''.join([''.join(__import__('random').choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))])}"
                await inputs[0].fill(username)
                print(f"Filled username: {username}")
                
                # Find and click submit
                submit_btn = await page.query_selector('button[type="submit"]')
                if submit_btn:
                    await submit_btn.click()
                    await page.wait_for_timeout(3000)
                    print("Submitted username")
                    print(f"New URL: {page.url}")
        
        # Check wallet/balance
        print("\n--- Checking wallet ---")
        wallet_page = await context.new_page()
        await wallet_page.goto("https://stacker.news/wallet", wait_until="networkidle")
        wallet_content = await wallet_page.content()
        with open('/home/user/income-quest/data/stacker_wallet.html', 'w') as f:
            f.write(wallet_content)
        
        wallet_url = wallet_page.url
        print(f"Wallet URL: {wallet_url}")
        
        # Look for balance, deposit, lightning address
        balance_matches = re.findall(r'(\d[\d,]*)\s*sats?', wallet_content, re.IGNORECASE)
        if balance_matches:
            print(f"Balance(s) found: {balance_matches}")
        
        ln_address_matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', wallet_content)
        if ln_address_matches:
            print(f"Lightning addresses found: {ln_address_matches[:10]}")
        
        # Check for deposit invoice
        if 'invoice' in wallet_content.lower() or 'deposit' in wallet_content.lower():
            print("Deposit/invoice options found")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())