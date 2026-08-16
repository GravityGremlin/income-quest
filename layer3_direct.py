#!/usr/bin/env python3
"""Try Layer3 wallet creation via direct URL or Get Started."""
import asyncio
from playwright.async_api import async_playwright

async def try_layer3_wallet():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Try direct wallet creation URL
        urls_to_try = [
            "https://layer3.xyz/wallet",
            "https://layer3.xyz/create-wallet",
            "https://layer3.xyz/signup",
            "https://layer3.xyz/activations",
            "https://app.layer3.xyz",
        ]
        
        for url in urls_to_try:
            print(f"\n=== Trying {url} ===")
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(5000)
                body_text = await page.inner_text('body')
                print(f"Content (first 3000): {body_text[:3000]}")
                
                # Look for wallet creation
                if "wallet" in body_text.lower() or "connect" in body_text.lower() or "sign" in body_text.lower():
                    print("  -> Found wallet/connect/sign keywords")
                    
                    # Try to find and click wallet creation
                    create_btns = await page.query_selector_all('button:has-text("Create"), button:has-text("Get Started"), button:has-text("Continue"), button:has-text("Layer3 Wallet")')
                    for btn in create_btns:
                        text = await btn.inner_text()
                        print(f"  Found button: {text.strip()}")
                        try:
                            await btn.click()
                            await page.wait_for_timeout(3000)
                            new_text = await page.inner_text('body')
                            print(f"  After click: {new_text[:2000]}")
                        except Exception as e:
                            print(f"  Click failed: {e}")
            except Exception as e:
                print(f"  Error: {e}")
        
        # Try clicking "Get Started" on main page
        print("\n=== Back to main page, clicking Get Started ===")
        await page.goto("https://layer3.xyz", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        get_started = await page.query_selector('button:has-text("Get Started"), a:has-text("Get Started")')
        if get_started:
            # Get the href if it's a link
            href = await get_started.get_attribute('href')
            tag = await get_started.evaluate('el => el.tagName')
            print(f"Get Started element: <{tag}> href={href}")
            
            if href and href.startswith('/'):
                await page.goto(f"https://layer3.xyz{href}", wait_until="networkidle")
            else:
                await get_started.click()
            await page.wait_for_timeout(5000)
            
            body_text = await page.inner_text('body')
            print(f"After Get Started: {body_text[:3000]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(try_layer3_wallet())