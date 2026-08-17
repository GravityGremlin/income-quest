#!/usr/bin/env python3
"""Try Layer3 Wallet creation - debug the Get Started flow."""
import asyncio
from playwright.async_api import async_playwright

async def layer3_wallet():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Go to main page
        print("Going to Layer3 main page...")
        await page.goto("https://layer3.xyz", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Find and click "Get Started" - get its href first
        get_started = await page.query_selector('a:has-text("Get Started"), button:has-text("Get Started")')
        if get_started:
            tag = await get_started.evaluate('el => el.tagName')
            href = await get_started.get_attribute('href')
            print(f"Get Started: <{tag}> href={href}")
            
            if href and href.startswith('/'):
                # Navigate directly
                await page.goto(f"https://layer3.xyz{href}", wait_until="networkidle")
            else:
                await get_started.click()
            await page.wait_for_timeout(5000)
        
        body_text = await page.inner_text('body')
        print(f"After Get Started: {body_text[:3000]}")
        
        # Look for wallet creation options
        wallet_btns = await page.query_selector_all('button:has-text("Layer3 Wallet"), button:has-text("Create Wallet"), button:has-text("Continue"), button:has-text("Get Started")')
        for btn in wallet_btns:
            text = await btn.inner_text()
            print(f"Wallet button: {text.strip()}")
            try:
                await btn.click()
                await page.wait_for_timeout(3000)
                new_text = await page.inner_text('body')
                print(f"After click: {new_text[:2000]}")
            except Exception as e:
                print(f"Click failed: {e}")
        
        # Check for any input fields (email, etc.)
        await page.wait_for_timeout(3000)
        body_text = await page.inner_text('body')
        print(f"Current state: {body_text[:3000]}")
        
        inputs = await page.query_selector_all('input')
        print(f"Input fields: {len(inputs)}")
        for inp in inputs:
            type_attr = await inp.get_attribute('type')
            name_attr = await inp.get_attribute('name')
            placeholder = await inp.get_attribute('placeholder')
            print(f"  Input: type={type_attr}, name={name_attr}, placeholder={placeholder}")
        
        # Try to find the actual wallet creation page
        print("\n--- Trying /wallet/create or similar ---")
        for path in ['/wallet/create', '/wallet', '/create-wallet', '/signup', '/onboarding']:
            try:
                await page.goto(f"https://layer3.xyz{path}", wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(3000)
                text = await page.inner_text('body')
                if 'wallet' in text.lower() or 'create' in text.lower() or 'email' in text.lower():
                    print(f"{path}: Found relevant content")
                    print(f"  {text[:1000]}")
            except Exception as e:
                print(f"{path}: Error - {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(layer3_wallet())