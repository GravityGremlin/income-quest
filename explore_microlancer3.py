#!/usr/bin/env python3
"""Explore Microlancer.io - wait for dynamic content."""
import asyncio
from playwright.async_api import async_playwright

async def explore_microlancer():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        print("🔍 Navigating to Microlancer.io...")
        await page.goto("https://microlancer.io", wait_until="networkidle", timeout=60000)
        
        # Wait longer for React to hydrate and fetch data
        await page.wait_for_timeout(10000)
        
        # Take screenshot
        await page.screenshot(path="/home/user/income-quest/microlancer_home.png", full_page=True)
        
        # Get body text after JS execution
        body_text = await page.inner_text('body')
        print(f"=== BODY TEXT (first 5000 chars) ===")
        print(body_text[:5000])
        
        # Check for any task-related content
        if 'task' in body_text.lower() or 'job' in body_text.lower() or 'gig' in body_text.lower():
            print("\n=== FOUND TASK/JOB/GIG KEYWORDS ===")
        
        # Check all links again after hydration
        all_links = await page.query_selector_all('a[href]')
        print(f"\nTotal links after hydration: {len(all_links)}")
        for link in all_links[:80]:
            href = await link.get_attribute('href')
            text = await link.inner_text()
            if text.strip():
                print(f"  {href} - {text.strip()[:100]}")
        
        # Try clicking "Browse" or similar if exists
        browse_buttons = await page.query_selector_all('button:has-text("Browse"), a:has-text("Browse"), button:has-text("Tasks"), a:has-text("Tasks")')
        for btn in browse_buttons:
            text = await btn.inner_text()
            print(f"Found browse/button: {text.strip()}")
            try:
                await btn.click()
                await page.wait_for_timeout(3000)
                new_text = await page.inner_text('body')
                print(f"After click, body text (first 2000): {new_text[:2000]}")
            except Exception as e:
                print(f"Click failed: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_microlancer())