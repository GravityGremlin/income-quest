#!/usr/bin/env python3
"""Find Stacker News login - check HTML directly."""
import asyncio
from playwright.async_api import async_playwright

async def check_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Go to Stacker News
        print("Going to Stacker News...")
        await page.goto("https://stacker.news", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Get full HTML
        html = await page.content()
        print(f"HTML length: {len(html)}")
        
        # Search for login/signup related strings
        import re
        for pattern in ['login', 'sign.?up', 'sign.?in', 'magic', 'email', 'auth', '/api/auth']:
            matches = [(m.start(), html[max(0,m.start()-100):m.end()+100]) for m in re.finditer(pattern, html, re.IGNORECASE)]
            if matches:
                print(f"\n=== '{pattern}' matches ({len(matches)}) ===")
                for pos, context in matches[:5]:
                    print(f"  Pos {pos}: ...{context}...")
        
        # Check for forms
        forms = await page.query_selector_all('form')
        print(f"\nForms: {len(forms)}")
        for form in forms:
            form_html = await form.inner_html()
            print(f"  Form: {form_html[:500]}")
        
        # Check for input elements
        inputs = await page.query_selector_all('input')
        print(f"\nInputs: {len(inputs)}")
        for inp in inputs:
            type_attr = await inp.get_attribute('type')
            name_attr = await inp.get_attribute('name')
            placeholder = await inp.get_attribute('placeholder')
            class_attr = await inp.get_attribute('class')
            print(f"  Input: type={type_attr}, name={name_attr}, placeholder={placeholder}, class={class_attr}")
        
        # Try direct navigation to common auth URLs
        for url in ['/login', '/signup', '/signin', '/register', '/auth/login', '/auth/signup', '/email']:
            print(f"\nTrying {url}...")
            try:
                await page.goto(f"https://stacker.news{url}", wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)
                body_text = await page.inner_text('body')
                if 'email' in body_text.lower() or 'code' in body_text.lower() or 'magic' in body_text.lower() or 'login' in body_text.lower() or 'sign' in body_text.lower():
                    print(f"  FOUND AUTH CONTENT: {body_text[:1000]}")
                else:
                    print(f"  Redirected to home")
            except Exception as e:
                print(f"  Error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_html())