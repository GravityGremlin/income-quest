#!/usr/bin/env python3
"""Explore Microlancer.io for Bitcoin/Lightning microtasks - enhanced version."""
import asyncio
import json
from playwright.async_api import async_playwright

async def explore_microlancer():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("🔍 Navigating to Microlancer.io...")
        await page.goto("https://microlancer.io", wait_until="networkidle", timeout=60000)
        
        # Wait for React/app to hydrate
        await page.wait_for_timeout(5000)
        
        # Take screenshot
        await page.screenshot(path="/home/user/income-quest/microlancer_home.png", full_page=True)
        
        # Get page content
        html = await page.content()
        print(f"Page title: {await page.title()}")
        print(f"Page length: {len(html)} chars")
        
        # Print first 5000 chars of HTML for analysis
        print("\n=== FIRST 5000 CHARS OF HTML ===")
        print(html[:5000])
        
        # Look for any text content
        body_text = await page.inner_text('body')
        print(f"\n=== BODY TEXT (first 3000 chars) ===")
        print(body_text[:3000])
        
        # Check for login/signup
        auth_links = await page.query_selector_all('a:has-text("Login"), a:has-text("Sign up"), a:has-text("Register"), a:has-text("Sign in"), a:has-text("Get Started")')
        for link in auth_links:
            text = await link.inner_text()
            href = await link.get_attribute('href')
            print(f"Auth: {text.strip()} -> {href}")
        
        # Check all links
        all_links = await page.query_selector_all('a[href]')
        print(f"\nTotal links: {len(all_links)}")
        for link in all_links[:50]:
            href = await link.get_attribute('href')
            text = await link.inner_text()
            if text.strip():
                print(f"  {href} - {text.strip()[:80]}")
        
        await browser.close()
        return html

if __name__ == "__main__":
    asyncio.run(explore_microlancer())