#!/usr/bin/env python3
"""
Complete Stacker News signup using Guerrilla Mail (sharklasers.com) temp email.
Uses Playwright for browser automation.
"""
import asyncio
import random
import string
import time
import json
from playwright.async_api import async_playwright


async def get_guerrilla_email(page):
    """Get a temporary email from Guerrilla Mail (sharklasers.com)."""
    await page.goto("https://www.guerrillamail.com/", wait_until="networkidle")
    await page.wait_for_timeout(3000)
    
    # The email address is displayed on the page
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
    
    # If not found via selectors, try to extract from page content
    if not email:
        content = await page.content()
        import re
        matches = re.findall(r'[a-zA-Z0-9._%+-]+@sharklasers\.com', content)
        if matches:
            email = matches[0]
    
    return email


async def check_guerrilla_inbox(page, email):
    """Check Guerrilla Mail inbox for magic code from Stacker News."""
    # Click refresh or just reload
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(3000)
    
    # Look for emails from Stacker News
    content = await page.content()
    
    # Search for magic code pattern (typically 6 digits or alphanumeric)
    import re
    # Look for Stacker News related emails
    sn_matches = re.findall(r'Stacker News.*?(\d{6})', content, re.IGNORECASE | re.DOTALL)
    if sn_matches:
        return sn_matches[0]
    
    # Generic 6-digit code patterns
    code_matches = re.findall(r'[Cc]ode[:\s]*(\d{6})', content)
    if code_matches:
        return code_matches[0]
    
    code_matches = re.findall(r'[Mm]agic[:\s]*(\d{6})', content)
    if code_matches:
        return code_matches[0]
    
    # Any 6-digit number in email context
    code_matches = re.findall(r'>(\d{6})<', content)
    if code_matches:
        return code_matches[0]
    
    # Look for any 6 digit number
    code_matches = re.findall(r'\b(\d{6})\b', content)
    if code_matches:
        # Filter out timestamps etc - look for codes near "code" or "magic" or "stacker"
        for code in code_matches:
            idx = content.find(code)
            context = content[max(0, idx-100):idx+100].lower()
            if any(kw in context for kw in ['code', 'magic', 'stacker', 'verify', 'login', 'sign']):
                return code
        # Return first if nothing else
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
        
        # Fill email field (name='email', type='text', class='form-control')
        email_input = await sn_page.wait_for_selector('input[name="email"]', timeout=10000)
        await email_input.fill(email)
        
        # Click "Continue with Email" button
        continue_btn = await sn_page.wait_for_selector('button:has-text("Continue with Email")', timeout=5000)
        await continue_btn.click()
        
        print("Signup submitted, waiting for magic code email...")
        
        # Wait and check for magic code
        max_attempts = 30
        magic_code = None
        
        for attempt in range(max_attempts):
            await asyncio.sleep(10)  # Wait 10 seconds between checks
            magic_code = await check_guerrilla_inbox(gm_page, email)
            if magic_code:
                print(f"Found magic code: {magic_code}")
                break
            print(f"Attempt {attempt + 1}/{max_attempts}: No code yet...")
        
        if not magic_code:
            print("Failed to get magic code")
            # Save debug info
            content = await gm_page.content()
            with open('/home/user/income-quest/data/guerrilla_debug.html', 'w') as f:
                f.write(content)
            await browser.close()
            return False
        
        # Enter magic code on Stacker News
        # The code input should appear after email submission
        code_input = await sn_page.wait_for_selector('input[name="code"], input[placeholder*="code" i], input[type="text"]', timeout=15000)
        await code_input.fill(magic_code)
        
        # Submit code - look for submit button
        code_submit = await sn_page.wait_for_selector('button[type="submit"]:has-text("Continue"), button[type="submit"]:has-text("Verify"), button[type="submit"]', timeout=5000)
        await code_submit.click()
        
        # Wait for redirect/completion
        await sn_page.wait_for_timeout(5000)
        
        # Check if logged in / profile page
        final_url = sn_page.url
        print(f"Final URL: {final_url}")
        
        # Try to set username if prompted
        try:
            username_input = await sn_page.wait_for_selector('input[name="username"]', timeout=5000)
            if username_input:
                # Generate a random username
                username = f"agent_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
                await username_input.fill(username)
                username_submit = await sn_page.wait_for_selector('button[type="submit"]', timeout=5000)
                await username_submit.click()
                print(f"Set username: {username}")
        except:
            pass  # Username might not be required or already set
        
        # Get session cookies for future use
        cookies = await context.cookies()
        stacker_cookies = [c for c in cookies if 'stacker.news' in c.get('domain', '')]
        print(f"Got {len(stacker_cookies)} Stacker News cookies")
        
        # Save cookies for future sessions
        with open('/home/user/income-quest/data/stacker_news_cookies.json', 'w') as f:
            json.dump(stacker_cookies, f)
        
        print("Stacker News signup completed!")
        await browser.close()
        return True


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)