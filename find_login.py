#!/usr/bin/env python3
"""Find Stacker News login flow."""
import asyncio
from playwright.async_api import async_playwright

async def find_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Go to Stacker News
        print("Going to Stacker News...")
        await page.goto("https://stacker.news", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Get all links
        all_links = await page.query_selector_all('a[href]')
        auth_links = []
        for link in all_links:
            href = await link.get_attribute('href')
            text = await link.inner_text()
            if text.strip() and ('login' in text.lower() or 'sign' in text.lower() or 'signin' in href.lower() or 'signup' in href.lower() or 'register' in href.lower() or 'auth' in href.lower() or 'email' in href.lower()):
                auth_links.append((href, text.strip()))
        
        print("Auth-related links:")
        for href, text in auth_links:
            print(f"  {href} - {text}")
        
        # Try each auth link
        for href, text in auth_links:
            print(f"\nTrying: {href} - {text}")
            try:
                full_url = href if href.startswith('http') else f"https://stacker.news{href}"
                await page.goto(full_url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)
                body_text = await page.inner_text('body')
                print(f"  Content (first 1000): {body_text[:1000]}")
                
                # Look for email input
                email_inputs = await page.query_selector_all('input[type="email"], input[name="email"]')
                if email_inputs:
                    print(f"  Found {len(email_inputs)} email input(s)!")
                    break
            except Exception as e:
                print(f"  Error: {e}")
        
        # Also check for buttons that might open login modal
        buttons = await page.query_selector_all('button')
        print(f"\nAll buttons: {len(buttons)}")
        for btn in buttons:
            text = await btn.inner_text()
            if text.strip() and ('login' in text.lower() or 'sign' in text.lower() or 'connect' in text.lower() or 'wallet' in text.lower()):
                class_attr = await btn.get_attribute('class')
                print(f"  Button: {text.strip()} | class={class_attr}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(find_login())