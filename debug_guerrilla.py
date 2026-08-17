#!/usr/bin/env python3
"""Debug Guerrilla Mail page."""
import asyncio
from playwright.async_api import async_playwright

async def debug_guerrilla():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        print("Going to Guerrilla Mail...")
        await page.goto("https://www.guerrillamail.com", wait_until="networkidle")
        await page.wait_for_timeout(5000)
        
        # Get full page text
        body_text = await page.inner_text('body')
        print(f"Page text (first 5000): {body_text[:5000]}")
        
        # Get all inputs
        inputs = await page.query_selector_all('input')
        print(f"\nInputs: {len(inputs)}")
        for inp in inputs:
            type_attr = await inp.get_attribute('type')
            name_attr = await inp.get_attribute('name')
            id_attr = await inp.get_attribute('id')
            value_attr = await inp.get_attribute('value')
            class_attr = await inp.get_attribute('class')
            print(f"  Input: type={type_attr}, name={name_attr}, id={id_attr}, value={value_attr}, class={class_attr}")
        
        # Get all elements with email-like content
        all_el = await page.query_selector_all('*')
        for el in all_el[:200]:
            try:
                text = await el.inner_text()
                if '@' in text and '.' in text and len(text) < 100:
                    tag = await el.evaluate('el => el.tagName')
                    class_attr = await el.get_attribute('class')
                    id_attr = await el.get_attribute('id')
                    print(f"  Email-like: <{tag} class={class_attr} id={id_attr}> {text.strip()}")
            except:
                pass
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_guerrilla())