#!/usr/bin/env python3
"""
Submit the magic code form via JavaScript.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        page = await context.new_page()
        
        # Listen to network
        page.on("request", lambda req: print(f"REQ: {req.method} {req.url}") if 'api' in req.url or 'auth' in req.url else None)
        page.on("response", lambda resp: print(f"RES: {resp.status} {resp.url}") if 'api' in resp.url or 'auth' in resp.url else None)
        
        await page.goto("https://stacker.news/email", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # Enable and fill inputs
        await page.evaluate('''
            document.querySelectorAll('input[name="token"]').forEach(el => {
                el.disabled = false;
                el.readOnly = false;
            });
        ''')
        
        # Fill code 123456
        await page.evaluate('''
            const inputs = document.querySelectorAll('input[name="token"]');
            const code = "123456";
            inputs.forEach((el, i) => { el.value = code[i]; });
        ''')
        
        # Submit via form submit event
        await page.evaluate('''
            const form = document.querySelector('form');
            if (form) {
                form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
            }
        ''')
        
        await page.wait_for_timeout(5000)
        print(f"URL after JS submit: {page.url}")
        
        # Check cookies
        cookies = await context.cookies()
        for c in cookies:
            if 'stacker' in c['domain']:
                print(f"  {c['name']} = {c['value'][:30]}...")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())