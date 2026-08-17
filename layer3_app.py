#!/usr/bin/env python3
"""Explore Layer3 app (app.layer3.xyz) and try to complete a free Learn quest."""
import asyncio
from playwright.async_api import async_playwright

async def layer3_app():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Go directly to the app discover page
        print("Going to app.layer3.xyz/discover...")
        await page.goto("https://app.layer3.xyz/discover", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        body_text = await page.inner_text('body')
        print(f"Discover page: {body_text[:3000]}")
        
        # Look for wallet connection
        connect_btns = await page.query_selector_all('button:has-text("Connect"), button:has-text("Wallet"), button:has-text("Layer3 Wallet"), button:has-text("Get Started")')
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
        print(f"After connect: {body_text[:3000]}")
        
        # Look for "Create Wallet" or similar in modal
        create_btns = await page.query_selector_all('button:has-text("Create"), button:has-text("Continue"), button:has-text("Let"), button:has-text("Start"), button:has-text("Generate")')
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
        print(f"Wallet state: {body_text[:3000]}")
        
        # Look for "Learn" category or free quests
        print("\n--- Looking for Learn quests ---")
        learn_elements = await page.query_selector_all('*:has-text("Learn"):not(script):not(style)')
        for el in learn_elements[:20]:
            text = await el.inner_text()
            if text.strip() and len(text.strip()) > 5:
                tag = await el.evaluate('el => el.tagName')
                print(f"  <{tag}>: {text.strip()[:100]}")
        
        # Try to find and click a "Learn" quest
        learn_links = await page.query_selector_all('a[href*="learn"], a[href*="intro"], button:has-text("Learn"), a:has-text("Introduction")')
        for link in learn_links[:10]:
            text = await link.inner_text()
            href = await link.get_attribute('href')
            print(f"Learn link: {text.strip()} -> {href}")
            if href:
                try:
                    full_url = href if href.startswith('http') else f"https://app.layer3.xyz{href}"
                    await page.goto(full_url, wait_until="networkidle")
                    await page.wait_for_timeout(5000)
                    quest_text = await page.inner_text('body')
                    print(f"Quest page: {quest_text[:2000]}")
                    
                    # Look for start/mint button
                    start_btns = await page.query_selector_all('button:has-text("Start"), button:has-text("Begin"), button:has-text("Mint"), button:has-text("Claim"), button:has-text("Complete"), button:has-text("Continue")')
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
    asyncio.run(layer3_app())