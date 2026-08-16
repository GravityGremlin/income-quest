#!/usr/bin/env python3
"""
Playwright script to thoroughly explore Coze signup page for email option.
"""
import asyncio
from playwright.async_api import async_playwright

async def explore_signup_thoroughly():
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
            
            # Get full page text
            page_text = await page.evaluate('() => document.body.innerText')
            print(f"\n=== FULL PAGE TEXT ===")
            print(page_text)
            
            # Get all element outerHTML for analysis
            all_html = await page.evaluate('() => document.body.outerHTML')
            with open("/tmp/coze_full_page.html", "w") as f:
                f.write(all_html)
            print(f"\nFull HTML saved to /tmp/coze_full_page.html ({len(all_html)} chars)")
            
            # Look for any hidden email fields or tabs
            print("\n=== SEARCHING FOR EMAIL/PHONE TOGGLE ===")
            elements = await page.query_selector_all('*')
            for el in elements:
                outer = await el.evaluate('el => el.outerHTML')
                if outer and any(kw in outer.lower() for kw in ['email', 'phone', 'tab', 'switch', 'toggle']):
                    if len(outer) < 500:
                        print(f"  {outer[:200]}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_signup_thoroughly())