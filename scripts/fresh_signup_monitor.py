#!/usr/bin/env python3
"""
Fresh signup with full network monitoring to find session token creation.
"""
import asyncio
import json
import random
import string
from playwright.async_api import async_playwright


async def get_guerrilla_email(page):
    await page.goto("https://www.guerrillamail.com/", wait_until="networkidle")
    await page.wait_for_timeout(3000)
    
    email_selectors = ['#email-widget', 'input[name="email"]', '#inbox-id', '.email-address', '[data-email]']
    email = None
    for selector in email_selectors:
        try:
            element = await page.wait_for_selector(selector, timeout=5000)
            email = await element.get_attribute('value') or await element.text_content()
            if email and '@' in email:
                email = email.strip()
                break
        except:
            continue
    
    if not email:
        content = await page.content()
        import re
        matches = re.findall(r'[a-zA-Z0-9._%+-]+@sharklasers\.com', content)
        if matches:
            email = matches[0]
    
    return email


async def check_guerrilla_inbox(page):
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(3000)
    content = await page.content()
    import re
    
    sn_matches = re.findall(r'Stacker News.*?(\d{6})', content, re.IGNORECASE | re.DOTALL)
    if sn_matches:
        return sn_matches[0]
    code_matches = re.findall(r'[Cc]ode[:\s]*(\d{6})', content)
    if code_matches:
        return code_matches[0]
    code_matches = re.findall(r'[Mm]agic[:\s]*(\d{6})', content)
    if code_matches:
        return code_matches[0]
    code_matches = re.findall(r'\b(\d{6})\b', content)
    if code_matches:
        for code in code_matches:
            idx = content.find(code)
            context = content[max(0, idx-100):idx+100].lower()
            if any(kw in context for kw in ['code', 'magic', 'stacker', 'verify', 'login', 'sign']):
                return code
        return code_matches[0]
    return None


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Monitor ALL requests/responses
        auth_requests = []
        auth_responses = []
        
        context.on("request", lambda req: auth_requests.append((req.method, req.url, req.post_data)) if any(kw in req.url for kw in ['auth', 'signin', 'callback', 'session', 'email', 'verify', 'magic']) else None)
        context.on("response", lambda resp: auth_responses.append((resp.status, resp.url)) if any(kw in resp.url for kw in ['auth', 'signin', 'callback', 'session', 'email', 'verify', 'magic']) else None)
        
        # Page 1: Guerrilla Mail
        gm_page = await context.new_page()
        print("Getting temp email...")
        email = await get_guerrilla_email(gm_page)
        print(f"Email: {email}")
        
        # Page 2: Stacker News signup
        sn_page = await context.new_page()
        await sn_page.goto("https://stacker.news/signup", wait_until="networkidle")
        
        # Fill email
        email_input = await sn_page.wait_for_selector('input[name="email"]', timeout=10000)
        await email_input.fill(email)
        
        # Click Continue with Email
        continue_btn = await sn_page.wait_for_selector('button:has-text("Continue with Email")', timeout=5000)
        await continue_btn.click()
        await sn_page.wait_for_timeout(3000)
        print(f"After email submit URL: {sn_page.url}")
        
        # Wait for magic code
        print("Waiting for magic code...")
        magic_code = None
        for attempt in range(30):
            await asyncio.sleep(10)
            magic_code = await check_guerrilla_inbox(gm_page)
            if magic_code:
                print(f"Found magic code: {magic_code}")
                break
            print(f"  Attempt {attempt+1}: waiting...")
        
        if not magic_code:
            print("No magic code received")
            await browser.close()
            return
        
        # Now on /email page - enable inputs and submit
        await sn_page.wait_for_timeout(2000)
        
        # Enable inputs via JS
        await sn_page.evaluate('''
            document.querySelectorAll('input[name="token"]').forEach(el => {
                el.disabled = false;
                el.readOnly = false;
            });
        ''')
        
        # Fill code
        await sn_page.evaluate(f'''
            const inputs = document.querySelectorAll('input[name="token"]');
            const code = "{magic_code}";
            inputs.forEach((el, i) => {{ el.value = code[i]; }});
        ''')
        
        # Submit via form
        await sn_page.evaluate('''
            const form = document.querySelector('form');
            if (form) {
                form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
            }
        ''')
        
        # Wait for redirect
        await sn_page.wait_for_timeout(10000)
        print(f"Final URL: {sn_page.url}")
        
        # Print auth-related network activity
        print("\n=== AUTH REQUESTS ===")
        for method, url, data in auth_requests:
            print(f"  {method} {url}")
            if data:
                print(f"    Data: {data[:200]}")
        
        print("\n=== AUTH RESPONSES ===")
        for status, url in auth_responses:
            print(f"  {status} {url}")
        
        # Check cookies
        cookies = await context.cookies()
        print(f"\n=== ALL COOKIES ({len(cookies)}) ===")
        for c in cookies:
            print(f"  {c['name']} @ {c['domain']} = {c['value'][:50]}...")
        
        # Save cookies
        with open('/home/user/income-quest/data/stacker_news_cookies_fresh.json', 'w') as f:
            json.dump(cookies, f)
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())