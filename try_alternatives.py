#!/usr/bin/env python3
"""
Playwright script to try email in phone field and explore alternatives.
"""
import asyncio
from playwright.async_api import async_playwright

async def try_email_in_phone_field():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
        )
        page = await context.new_page()
        
        try:
            print("Navigating to Coze signup...")
            await page.goto("https://www.coze.com/sign?redirect=%2Fhome", wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(2000)
            
            # Try typing email in phone field
            print("Trying to type email in phone field...")
            phone_input = await page.query_selector('input[placeholder="Phone number"]')
            if phone_input:
                await phone_input.fill("test@example.com")
                await page.wait_for_timeout(1000)
                # Check if validation error appears
                page_text = await page.evaluate('() => document.body.innerText')
                print(f"Page text after email input:\n{page_text}")
            
            # Check country code selector
            print("\n=== Looking for country code selector ===")
            country_selectors = await page.query_selector_all('[class*="country"], [class*="select"], [role="combobox"], button:has-text("+1")')
            for sel in country_selectors:
                text = await sel.inner_text()
                print(f"  Found: '{text}'")
                # Try clicking
                try:
                    await sel.click()
                    await page.wait_for_timeout(1000)
                    page_text = await page.evaluate('() => document.body.innerText')
                    print(f"After click:\n{page_text[:500]}")
                except:
                    pass
            
            # Check coze.cn
            print("\n=== Checking coze.cn ===")
            await page.goto("https://www.coze.cn", wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)
            page_text = await page.evaluate('() => document.body.innerText')
            print(f"coze.cn text (first 2000 chars):\n{page_text[:2000]}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(try_email_in_phone_field())