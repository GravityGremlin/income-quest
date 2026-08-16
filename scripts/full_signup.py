#!/usr/bin/env python3
"""
Complete Stacker News signup with full session capture.
"""
import asyncio
import json
import random
import string
from playwright.async_api import async_playwright


async def get_guerrilla_email(page):
    """Get a temporary email from Guerrilla Mail (sharklasers.com)."""
    await page.goto("https://www.guerrillamail.com/", wait_until="networkidle")
    await page.wait_for_timeout(3000)
    
    email_selectors = [
        '#email-widget',
        'input[name="email"]',
        '#inbox-id',
        '.email-address',
        '[data-email]'
    ]
    
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
    """Check Guerrilla Mail inbox for magic code."""
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(3000)
    
    content = await page.content()
    import re
    
    # Look for Stacker News magic code
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
        
        # Page 1: Guerrilla Mail for temp email
        gm_page = await context.new_page()
        print("Getting temp email from Guerrilla Mail...")
        email = await get_guerrilla_email(gm_page)
        
        if not email:
            print("Failed to get temp email")
            await browser.close()
            return False
        
        print(f"Got temp email: {email}")
        
        # Page 2: Stacker News signup
        sn_page = await context.new_page()
        await sn_page.goto("https://stacker.news/signup", wait_until="networkidle")
        
        # Fill email field
        email_input = await sn_page.wait_for_selector('input[name="email"]', timeout=10000)
        await email_input.fill(email)
        
        # Click "Continue with Email"
        continue_btn = await sn_page.wait_for_selector('button:has-text("Continue with Email")', timeout=5000)
        await continue_btn.click()
        
        print("Signup submitted, waiting for magic code email...")
        
        # Wait and check for magic code
        max_attempts = 30
        magic_code = None
        
        for attempt in range(max_attempts):
            await asyncio.sleep(10)
            magic_code = await check_guerrilla_inbox(gm_page)
            if magic_code:
                print(f"Found magic code: {magic_code}")
                break
            print(f"Attempt {attempt + 1}/{max_attempts}: No code yet...")
        
        if not magic_code:
            print("Failed to get magic code")
            await browser.close()
            return False
        
        # Enter magic code on the /email page (or wherever we are)
        # The form has input[name="token"]
        token_input = await sn_page.wait_for_selector('input[name="token"]', timeout=15000)
        await token_input.fill(magic_code)
        
        # Submit
        submit_btn = await sn_page.wait_for_selector('button[type="submit"]', timeout=5000)
        await submit_btn.click()
        
        # Wait for redirect
        await sn_page.wait_for_timeout(5000)
        
        print(f"After code submit URL: {sn_page.url}")
        
        # Check if we need to set username
        if 'username' in sn_page.url or 'settings' in sn_page.url or 'profile' in sn_page.url:
            print("Username setup page detected")
            username_input = await sn_page.wait_for_selector('input[name="username"], input[name="name"]', timeout=5000)
            if username_input:
                username = f"agent_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
                await username_input.fill(username)
                username_submit = await sn_page.wait_for_selector('button[type="submit"]', timeout=5000)
                await username_submit.click()
                await sn_page.wait_for_timeout(3000)
                print(f"Set username: {username}")
        
        # Get ALL cookies
        cookies = await context.cookies()
        print(f"Total cookies: {len(cookies)}")
        for c in cookies:
            print(f"  {c['name']} @ {c['domain']}")
        
        # Save all cookies
        with open('/home/user/income-quest/data/stacker_news_cookies_full.json', 'w') as f:
            json.dump(cookies, f)
        
        # Also save stacker.news specific cookies
        stacker_cookies = [c for c in cookies if 'stacker.news' in c.get('domain', '')]
        with open('/home/user/income-quest/data/stacker_news_cookies.json', 'w') as f:
            json.dump(stacker_cookies, f)
        
        print(f"Saved {len(stacker_cookies)} Stacker News cookies")
        
        # Test wallet access
        wallet_page = await context.new_page()
        await wallet_page.goto("https://stacker.news/wallet", wait_until="networkidle")
        await wallet_page.wait_for_timeout(2000)
        wallet_text = await wallet_page.text_content('body')
        print(f"\nWallet page text: {wallet_text[:500]}")
        
        await browser.close()
        return True


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)