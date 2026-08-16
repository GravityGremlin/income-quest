#!/usr/bin/env python3
"""
Debug the magic code submission on /email page - check network requests.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Load existing cookies
        with open('/home/user/income-quest/data/stacker_news_cookies_full.json', 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        # Listen to network requests
        page.on("request", lambda req: print(f"REQ: {req.method} {req.url}") if 'stacker' in req.url else None)
        page.on("response", lambda resp: print(f"RES: {resp.status} {resp.url}") if 'stacker' in resp.url else None)
        
        await page.goto("https://stacker.news/email", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        # Fill token input with a dummy code to see what happens
        token_inputs = await page.query_selector_all('input[name="token"]')
        print(f"Token inputs: {len(token_inputs)}")
        
        if token_inputs:
            await token_inputs[0].fill("123456")
            
            # Click submit and watch network
            submit_btn = await page.query_selector('button[type="submit"]')
            if submit_btn:
                print("Clicking submit...")
                await submit_btn.click()
                await page.wait_for_timeout(5000)
                print(f"URL after submit: {page.url}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())