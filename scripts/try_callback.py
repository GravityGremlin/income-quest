#!/usr/bin/env python3
"""
Try submitting magic code to NextAuth callback endpoint directly.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # First, get the csrf token
        page = await context.new_page()
        await page.goto("https://stacker.news/api/auth/csrf", wait_until="networkidle")
        csrf_data = await page.text_content('body')
        print(f"CSRF: {csrf_data}")
        
        # Try the callback endpoint with a magic code
        # NextAuth email provider typically uses: POST /api/auth/callback/email with token
        callback_url = "https://stacker.news/api/auth/callback/email"
        
        # We need a valid magic code. Let's use the one we got: 949494
        # But it might be expired. Let's try anyway.
        
        # The callback typically expects: token=<magic_code>&csrfToken=<csrf>
        import urllib.parse
        
        csrf_token = ""
        try:
            csrf_json = json.loads(csrf_data)
            csrf_token = csrf_json.get('csrfToken', '')
        except:
            pass
        
        print(f"CSRF Token: {csrf_token[:30]}...")
        
        # Submit via fetch
        result = await page.evaluate(f'''
            return fetch("{callback_url}", {{
                method: "POST",
                headers: {{
                    "Content-Type": "application/x-www-form-urlencoded",
                }},
                body: "token=949494&csrfToken={csrf_token}&callbackUrl=https%3A%2F%2Fstacker.news%2F&json=true"
            }}).then(r => r.json());
        ''')
        
        print(f"Callback result: {json.dumps(result, indent=2)}")
        
        # Check cookies after
        cookies = await context.cookies()
        for c in cookies:
            if 'stacker' in c['domain']:
                print(f"  {c['name']} = {c['value'][:50]}...")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())