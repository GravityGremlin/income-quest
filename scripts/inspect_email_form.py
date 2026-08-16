#!/usr/bin/env python3
"""
Inspect the /email page form structure.
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
        await page.wait_for_timeout(2000)
        
        # Get the form HTML
        forms = await page.query_selector_all('form')
        print(f"Forms found: {len(forms)}")
        for i, form in enumerate(forms):
            html = await form.evaluate('el => el.outerHTML')
            print(f"\nForm {i}:")
            print(html[:2000])
        
        # Get all inputs with details
        inputs = await page.query_selector_all('input')
        print(f"\nInputs: {len(inputs)}")
        for inp in inputs:
            attrs = await inp.evaluate('el => ({name: el.name, type: el.type, placeholder: el.placeholder, id: el.id, value: el.value, form: el.form?.action, formMethod: el.form?.method})')
            print(f"  {attrs}")
        
        # Check buttons
        buttons = await page.query_selector_all('button')
        print(f"\nButtons: {len(buttons)}")
        for btn in buttons:
            attrs = await btn.evaluate('el => ({type: el.type, text: el.textContent, class: el.className, form: el.form?.action})')
            print(f"  {attrs}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())