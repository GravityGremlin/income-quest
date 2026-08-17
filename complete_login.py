#!/usr/bin/env python3
"""Complete Stacker News login with the found magic code."""
import asyncio
import re
from playwright.async_api import async_playwright

async def complete_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path="/usr/bin/chromium", args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # The magic code we found
        magic_code = "rrkpd6"
        print(f"Using magic code: {magic_code}")
        
        # Go to email verification page
        await page.goto("https://stacker.news/email", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        code_inputs = await page.query_selector_all('input[name="code"], input[placeholder*="code" i], input[type="text"], input[maxlength="6"]')
        for inp in code_inputs:
            try:
                await inp.fill(magic_code)
                print(f"Filled magic code: {magic_code}")
            except Exception as e:
                print(f"Fill failed: {e}")
        
        submit_btns = await page.query_selector_all('button[type="submit"], button:has-text("Submit"), button:has-text("Verify"), button:has-text("Login"), button:has-text("Continue")')
        for btn in submit_btns:
            try:
                await btn.click()
                print("Submitted magic code")
                await page.wait_for_timeout(5000)
                break
            except Exception as e:
                print(f"Click failed: {e}")
        
        # Check if logged in
        await page.goto("https://stacker.news", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        body_text = await page.inner_text('body')
        print(f"After login: {body_text[:3000]}")
        
        # Check wallet
        wallet_links = await page.query_selector_all('a:has-text("Wallet"), a:has-text("wallet"), a[href*="wallet"], a[href*="@"]')
        for link in wallet_links:
            text = await link.inner_text()
            href = await link.get_attribute('href')
            print(f"Wallet link: {text.strip()} -> {href}")
            if href:
                await page.goto(href if href.startswith('http') else f"https://stacker.news{href}", wait_until="networkidle")
                await page.wait_for_timeout(3000)
                wallet_text = await page.inner_text('body')
                print(f"Wallet page: {wallet_text[:2000]}")
        
        # Check for username/profile
        profile_links = await page.query_selector_all('a[href^="/@"], a:has-text("@")')
        for link in profile_links[:10]:
            text = await link.inner_text()
            href = await link.get_attribute('href')
            print(f"Profile link: {text.strip()} -> {href}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(complete_login())