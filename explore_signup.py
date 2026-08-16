#!/usr/bin/env python3
"""
Playwright script to explore Coze signup page interactively.
"""
import asyncio
from playwright.async_api import async_playwright

async def explore_signup_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
        )
        page = await context.new_page()
        
        try:
            print("Navigating to Coze signup...")
            await page.goto("https://www.coze.com/sign?redirect=%2Fhome", wait_until="networkidle", timeout=60000)
            print(f"URL: {page.url}")
            await page.wait_for_timeout(3000)
            
            # Take screenshot
            await page.screenshot(path="/tmp/coze_sign_page.png", full_page=True)
            
            # Look for all clickable elements with text
            print("\n=== ALL CLICKABLE ELEMENTS WITH TEXT ===")
            elements = await page.query_selector_all('button, a, [role="button"], [role="tab"]')
            for el in elements:
                text = await el.inner_text()
                tag = await el.evaluate('el => el.tagName')
                class_attr = await el.get_attribute('class')
                if text and text.strip():
                    print(f"  {tag}.{class_attr[:50] if class_attr else ''}: '{text.strip()[:100]}'")
            
            # Look for text containing email/phone/switch
            print("\n=== TEXT CONTAINING EMAIL/PHONE/SWITCH ===")
            all_text_elements = await page.query_selector_all('*')
            for el in all_text_elements:
                text = await el.inner_text()
                if text and any(kw in text.lower() for kw in ['email', 'phone', 'switch', 'instead', 'or ', 'tab']):
                    if len(text.strip()) < 200:
                        tag = await el.evaluate('el => el.tagName')
                        print(f"  {tag}: '{text.strip()}'")
            
            # Check for Google OAuth
            print("\n=== GOOGLE OAUTH ===")
            google_btn = await page.query_selector('button:has-text("google" i), button:has-text("Google" i)')
            if google_btn:
                print("Found Google OAuth button")
            else:
                print("No Google OAuth button found with text search")
                # Try by class or other attributes
                buttons = await page.query_selector_all('button')
                for btn in buttons:
                    class_attr = await btn.get_attribute('class') or ''
                    if 'google' in class_attr.lower():
                        print(f"  Found button with google in class: {class_attr}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path="/tmp/coze_error.png", full_page=True)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_signup_page())