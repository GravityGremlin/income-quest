#!/usr/bin/env python3
"""
Playwright script to try Google OAuth signup for Coze.
"""
import asyncio
from playwright.async_api import async_playwright

async def try_google_oauth():
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
            
            # Click "Continue with google"
            print("Clicking 'Continue with google'...")
            await page.click('button:has-text("Continue with google")', timeout=10000)
            await page.wait_for_timeout(3000)
            
            print(f"After Google click, URL: {page.url}")
            
            # Take screenshot
            await page.screenshot(path="/tmp/coze_google_oauth.png", full_page=True)
            
            # Check if we're on Google OAuth page
            if 'accounts.google.com' in page.url or 'oauth' in page.url.lower():
                print("Redirected to Google OAuth page")
                # Print page content
                content = await page.content()
                print(f"Google page content length: {len(content)}")
                with open("/tmp/coze_google_page.html", "w") as f:
                    f.write(content)
            else:
                print("Still on Coze page or different redirect")
                content = await page.content()
                with open("/tmp/coze_after_google_click.html", "w") as f:
                    f.write(content)
            
            # Look for any email/phone switch on the original page
            print("\n=== Checking for email signup option ===")
            # Go back to signup page
            await page.goto("https://www.coze.com/sign?redirect=%2Fhome", wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(2000)
            
            # Check all text on page for email/phone switch
            page_text = await page.evaluate('() => document.body.innerText')
            print(f"Page text length: {len(page_text)}")
            # Search for email/phone related text
            for line in page_text.split('\n'):
                if any(kw in line.lower() for kw in ['email', 'phone', 'switch', 'instead', 'or use', 'sign up with']):
                    print(f"  Found: '{line.strip()}'")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path="/tmp/coze_error.png", full_page=True)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(try_google_oauth())