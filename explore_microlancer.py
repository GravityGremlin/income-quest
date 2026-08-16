#!/usr/bin/env python3
"""Explore Microlancer.io for Bitcoin/Lightning microtasks."""
import asyncio
import json
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
        
        # Take screenshot
        await page.screenshot(path="/home/user/income-quest/microlancer_home.png", full_page=True)
        
        # Get page content
        html = await page.content()
        print(f"Page title: {await page.title()}")
        print(f"Page length: {len(html)} chars")
        
        # Look for task listings
        tasks = await page.query_selector_all('a[href*="/task"], a[href*="/job"], a[href*="/gig"], .task, .job, .gig, [class*="task"], [class*="job"], [class*="gig"]')
        print(f"Found {len(tasks)} potential task elements")
        
        # Look for navigation
        nav_links = await page.query_selector_all('nav a, header a, .nav a, .menu a')
        print(f"Navigation links: {len(nav_links)}")
        for link in nav_links[:20]:
            text = await link.inner_text()
            href = await link.get_attribute('href')
            if text.strip():
                print(f"  - {text.strip()[:50]} -> {href}")
        
        # Check for "Browse Tasks" or similar
        browse_links = await page.query_selector_all('a:has-text("Browse"), a:has-text("Tasks"), a:has-text("Jobs"), a:has-text("Marketplace")')
        for link in browse_links:
            text = await link.inner_text()
            href = await link.get_attribute('href')
            print(f"Browse link: {text.strip()} -> {href}")
        
        # Try to find task categories or search
        await page.wait_for_timeout(2000)
        
        # Scroll to load more
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight/3)")
            await page.wait_for_timeout(1000)
        
        # Get all links
        all_links = await page.query_selector_all('a[href]')
        task_urls = set()
        for link in all_links:
            href = await link.get_attribute('href')
            text = await link.inner_text()
            if href and ('task' in href.lower() or 'job' in href.lower() or 'gig' in href.lower()):
                task_urls.add((href, text.strip()[:80]))
        
        print(f"\nTask-related URLs found: {len(task_urls)}")
        for url, text in list(task_urls)[:20]:
            print(f"  {url} - {text}")
        
        # Check if there's a login/signup
        auth_links = await page.query_selector_all('a:has-text("Login"), a:has-text("Sign up"), a:has-text("Register"), a:has-text("Sign in")')
        for link in auth_links:
            text = await link.inner_text()
            href = await link.get_attribute('href')
            print(f"Auth: {text.strip()} -> {href}")
        
        await browser.close()
        return html

if __name__ == "__main__":
    asyncio.run(explore_microlancer())