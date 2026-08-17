#!/usr/bin/env python3
"""Try Layer3 Wallet creation - simpler approach."""
import asyncio
from playwright.async_api import async_playwright

async def layer3_wallet():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Go directly to activations page which showed quests
        print("Going to Layer3 activations...")
        await page.goto("https://layer3.xyz/activations", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        body_text = await page.inner_text('body')
        print(f"Activations page: {body_text[:3000]}")
        
        # Look for "Connect Wallet" or "Get Started" buttons
        connect_btns = await page.query_selector_all('button:has-text("Connect"), button:has-text("Get Started"), button:has-text("Layer3 Wallet"), a:has-text("Connect"), a:has-text("Get Started")')
        for btn in connect_btns:
            text = await btn.inner_text()
            print(f"Connect button: {text.strip()}")
            try:
                await btn.click()
                await page.wait_for_timeout(3000)
                new_text = await page.inner_text('body')
                print(f"After click: {new_text[:2000]}")
            except Exception as e:
                print(f"Click failed: {e}")
        
        # Check for wallet creation modal
        await page.wait_for_timeout(3000)
        body_text = await page.inner_text('body')
        print(f"After connect attempts: {body_text[:3000]}")
        
        # Look for "Create Wallet" or "Continue" in modal
        create_btns = await page.query_selector_all('button:has-text("Create"), button:has-text("Continue"), button:has-text("Let"), button:has-text("Start")')
        for btn in create_btns:
            text = await btn.inner_text()
            print(f"Create button: {text.strip()}")
            try:
                await btn.click()
                await page.wait_for_timeout(3000)
                new_text = await page.inner_text('body')
                print(f"After create click: {new_text[:2000]}")
            except Exception as e:
                print(f"Click failed: {e}")
        
        # Check if wallet created
        await page.wait_for_timeout(3000)
        body_text = await page.inner_text('body')
        print(f"Final state: {body_text[:3000]}")
        
        # If wallet exists, try to do a "Learn" quest
        if 'wallet' in body_text.lower() or 'cube' in body_text.lower() or 'address' in body_text.lower() or 'balance' in body_text.lower():
            print("\nWallet seems connected! Looking for Learn quests...")
            
            # Find Learn quest links
            learn_links = await page.query_selector_all('a:has-text("Learn"), a:has-text("Introduction"), a[href*="learn"], a[href*="intro"]')
            for link in learn_links[:10]:
                text = await link.inner_text()
                href = await link.get_attribute('href')
                print(f"Learn quest: {text.strip()} -> {href}")
                if href:
                    try:
                        full_url = href if href.startswith('http') else f"https://layer3.xyz{href}"
                        await page.goto(full_url, wait_until="networkidle")
                        await page.wait_for_timeout(5000)
                        quest_text = await page.inner_text('body')
                        print(f"Quest page: {quest_text[:2000]}")
                        
                        # Look for start button
                        start_btns = await page.query_selector_all('button:has-text("Start"), button:has-text("Begin"), button:has-text("Mint"), button:has-text("Claim"), button:has-text("Complete")')
                        for sbtn in start_btns:
                            stext = await sbtn.inner_text()
                            print(f"  Start button: {stext.strip()}")
                            try:
                                await sbtn.click()
                                await page.wait_for_timeout(5000)
                                result = await page.inner_text('body')
                                print(f"  Result: {result[:2000]}")
                            except Exception as e:
                                print(f"  Click failed: {e}")
                        break
                    except Exception as e:
                        print(f"Quest navigation failed: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(layer3_wallet())