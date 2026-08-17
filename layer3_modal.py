#!/usr/bin/env python3
"""Explore Layer3 Connect Wallet modal in detail."""
import asyncio
from playwright.async_api import async_playwright

async def layer3_modal():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Go to app
        print("Going to app.layer3.xyz/discover...")
        await page.goto("https://app.layer3.xyz/discover", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Click "Sign up" to open modal
        signup_btn = await page.query_selector('button:has-text("Sign up"), a:has-text("Sign up")')
        if signup_btn:
            await signup_btn.click()
            await page.wait_for_timeout(3000)
            print("Clicked Sign up")
        
        # Wait for modal and get all elements in it
        await page.wait_for_timeout(2000)
        
        # Find modal
        modals = await page.query_selector_all('[role="dialog"], .modal, [class*="modal"], [class*="Modal"], [class*="wallet"], [class*="Wallet"]')
        print(f"Modals found: {len(modals)}")
        for modal in modals:
            text = await modal.inner_text()
            print(f"Modal content: {text[:1000]}")
            html = await modal.inner_html()
            print(f"Modal HTML: {html[:2000]}")
        
        # Get all buttons in the page (modal buttons)
        all_buttons = await page.query_selector_all('button')
        print(f"\nAll buttons: {len(all_buttons)}")
        for btn in all_buttons:
            text = await btn.inner_text()
            if text.strip():
                class_attr = await btn.get_attribute('class')
                print(f"  Button: {text.strip()[:80]} | class={class_attr}")
        
        # Get all clickable elements
        clickable = await page.query_selector_all('button, a[href], [role="button"], [tabindex="0"]')
        print(f"\nClickable elements: {len(clickable)}")
        for el in clickable:
            text = await el.inner_text()
            tag = await el.evaluate('el => el.tagName')
            href = await el.get_attribute('href')
            class_attr = await el.get_attribute('class')
            if text.strip() and ('wallet' in text.lower() or 'layer3' in text.lower() or 'email' in text.lower() or 'create' in text.lower() or 'continue' in text.lower() or 'bitcoin' in text.lower() or 'ethereum' in text.lower() or 'solana' in text.lower()):
                print(f"  <{tag}> class={class_attr} href={href}: {text.strip()[:100]}")
        
        # Try clicking "Bitcoin" wallet option
        bitcoin_btn = await page.query_selector('button:has-text("Bitcoin"), button:has-text("bitcoin")')
        if bitcoin_btn:
            print("\nClicking Bitcoin wallet option...")
            await bitcoin_btn.click()
            await page.wait_for_timeout(3000)
            body_text = await page.inner_text('body')
            print(f"After Bitcoin click: {body_text[:2000]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(layer3_modal())