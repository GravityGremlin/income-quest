#!/usr/bin/env python3
"""
Playwright script to explore Coze signup page structure.
"""
import asyncio
from playwright.async_api import async_playwright

async def explore_coze():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
        )
        page = await context.new_page()
        
        try:
            print("Navigating to Coze...")
            await page.goto("https://www.coze.com", wait_until="networkidle", timeout=60000)
            print(f"URL: {page.url}")
            
            # Wait a bit for dynamic content
            await page.wait_for_timeout(3000)
            
            # Get all buttons and links
            buttons = await page.query_selector_all('button')
            links = await page.query_selector_all('a')
            
            print("\n=== BUTTONS ===")
            for btn in buttons:
                text = await btn.inner_text()
                if text.strip():
                    print(f"  Button: '{text.strip()}'")
            
            print("\n=== LINKS ===")
            for link in links[:30]:
                text = await link.inner_text()
                href = await link.get_attribute('href')
                if text.strip():
                    print(f"  Link: '{text.strip()}' -> {href}")
            
            # Look for signup-related elements
            print("\n=== SIGNUP RELATED ===")
            all_elements = await page.query_selector_all('*')
            for el in all_elements:
                text = await el.inner_text()
                if text and ('sign up' in text.lower() or 'signup' in text.lower() or 'register' in text.lower() or 'get started' in text.lower()):
                    tag = await el.evaluate('el => el.tagName')
                    print(f"  {tag}: '{text.strip()[:100]}'")
            
            # Take screenshot
            await page.screenshot(path="/tmp/coze_home.png", full_page=True)
            print("\nScreenshot saved to /tmp/coze_home.png")
            
        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path="/tmp/coze_error.png", full_page=True)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_coze())