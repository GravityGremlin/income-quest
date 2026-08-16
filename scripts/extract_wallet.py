#!/usr/bin/env python3
"""
Extract rendered wallet page content after JS execution.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Load cookies
        with open('/home/user/income-quest/data/stacker_news_cookies.json', 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        await page.goto("https://stacker.news/wallet", wait_until="networkidle")
        await page.wait_for_timeout(3000)  # Wait for JS to render
        
        # Get fully rendered content
        content = await page.content()
        with open('/home/user/income-quest/data/stacker_wallet_rendered.html', 'w') as f:
            f.write(content)
        
        # Extract text content
        text = await page.text_content('body')
        print("=== WALLET PAGE TEXT ===")
        print(text[:5000])
        
        # Look for buttons/links related to deposit/withdraw
        buttons = await page.query_selector_all('button, a')
        print("\n=== BUTTONS/LINKS ===")
        for btn in buttons:
            text = await btn.text_content()
            href = await btn.get_attribute('href')
            cls = await btn.get_attribute('class')
            if any(kw in (text or '').lower() for kw in ['deposit', 'withdraw', 'invoice', 'lightning', 'receive', 'send', 'zap', 'balance']):
                print(f"  text='{text}', href='{href}', class='{cls}'")
        
        # Check for lightning address display
        all_text = await page.text_content('body')
        import re
        ln_addrs = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', all_text)
        if ln_addrs:
            print(f"\nLightning addresses: {ln_addrs}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())