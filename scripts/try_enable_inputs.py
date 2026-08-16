#!/usr/bin/env python3
"""
Check why inputs are disabled and try to enable them.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        page = await context.new_page()
        await page.goto("https://stacker.news/email", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # Check if inputs are disabled via JS
        inputs = await page.query_selector_all('input[name="token"]')
        for i, inp in enumerate(inputs):
            disabled = await inp.get_attribute('disabled')
            print(f"Input {i} disabled: {disabled}")
        
        # Try to enable via JS
        await page.evaluate('''
            document.querySelectorAll('input[name="token"]').forEach(el => {
                el.disabled = false;
                el.readOnly = false;
            });
        ''')
        
        # Check again
        for i, inp in enumerate(inputs):
            disabled = await inp.get_attribute('disabled')
            print(f"Input {i} disabled after JS: {disabled}")
        
        # Now try to fill
        if inputs:
            await inputs[0].fill("1")
            await inputs[1].fill("2")
            await inputs[2].fill("3")
            await inputs[3].fill("4")
            await inputs[4].fill("5")
            await inputs[5].fill("6")
            print("Filled code 123456")
            
            # Find submit button
            submit_btn = await page.query_selector('button[type="submit"]')
            if submit_btn:
                await submit_btn.click()
                await page.wait_for_timeout(5000)
                print(f"URL after submit: {page.url}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())