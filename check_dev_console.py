#!/usr/bin/env python3
"""
Playwright script to check coze.cn and developer signup.
"""
import asyncio
from playwright.async_api import async_playwright

async def check_coze_cn_and_dev():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
        )
        page = await context.new_page()
        
        try:
            print("=== Checking coze.cn ===")
            await page.goto("https://www.coze.cn", wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)
            page_text = await page.evaluate('() => document.body.innerText')
            print(f"coze.cn text (first 3000 chars):\n{page_text[:3000]}")
            
            # Check developer console directly
            print("\n=== Checking developer console (coze.com/open/oauth/pats) ===")
            await page.goto("https://www.coze.com/open/oauth/pats", wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)
            page_text = await page.evaluate('() => document.body.innerText')
            print(f"Developer console text (first 3000 chars):\n{page_text[:3000]}")
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # If redirected to login, check login page
            if 'sign' in current_url or 'login' in current_url:
                print("\n=== Login page text ===")
                page_text = await page.evaluate('() => document.body.innerText')
                print(page_text[:3000])
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_coze_cn_and_dev())