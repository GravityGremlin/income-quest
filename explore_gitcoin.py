#!/usr/bin/env python3
"""Explore Gitcoin bounties for developer tasks."""
import asyncio
from playwright.async_api import async_playwright

async def explore_gitcoin():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        print("🔍 Navigating to Gitcoin.co...")
        await page.goto("https://gitcoin.co", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        await page.screenshot(path="/home/user/income-quest/gitcoin_home.png", full_page=True)
        
        body_text = await page.inner_text('body')
        print(f"=== BODY TEXT (first 5000) ===")
        print(body_text[:5000])
        
        # Look for bounties
        all_links = await page.query_selector_all('a[href]')
        bounty_links = []
        for link in all_links[:100]:
            href = await link.get_attribute('href')
            text = await link.inner_text()
            if text.strip() and ('bounty' in text.lower() or 'bounty' in href.lower() or 'grant' in text.lower() or 'grant' in href.lower() or 'earn' in text.lower() or 'work' in text.lower()):
                bounty_links.append((href, text.strip()[:100]))
        
        print(f"Bounty-related links: {len(bounty_links)}")
        for href, text in bounty_links[:20]:
            print(f"  {href} - {text}")
        
        # Check for login/connect
        auth_btns = await page.query_selector_all('button:has-text("Connect"), button:has-text("Login"), button:has-text("Sign in"), a:has-text("Connect"), a:has-text("Login")')
        for btn in auth_btns:
            text = await btn.inner_text()
            print(f"Auth button: {text.strip()}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_gitcoin())