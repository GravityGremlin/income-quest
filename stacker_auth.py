#!/usr/bin/env python3
"""Complete Stacker News authentication and earn sats."""
import asyncio
import re
from playwright.async_api import async_playwright

async def stacker_news_auth():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Go to Guerrilla Mail to get the same email we used before
        print("Going to Guerrilla Mail to check for magic code...")
        await page.goto("https://www.guerrillamail.com", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # The email we used before was from sharklasers.com
        # Let's try to access the inbox for that email
        email_addr = "y9w9rr+62jmn93n5n7k0@sharklasers.com"  # from last run
        print(f"Using email: {email_addr}")
        
        # Go to Stacker News and request magic code for this email
        print("\nGoing to Stacker News...")
        await page.goto("https://stacker.news", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Click login
        login_btn = await page.query_selector('a:has-text("Login"), button:has-text("Login"), a:has-text("Sign in")')
        if login_btn:
            await login_btn.click()
            await page.wait_for_timeout(2000)
            print("Clicked Login")
        
        # Find email input
        email_inputs = await page.query_selector_all('input[type="email"], input[name="email"], input[placeholder*="email" i]')
        for inp in email_inputs:
            try:
                await inp.fill(email_addr)
                print(f"Filled email: {email_addr}")
            except Exception as e:
                print(f"Fill failed: {e}")
        
        # Submit magic code request
        submit_btns = await page.query_selector_all('button[type="submit"], button:has-text("Send"), button:has-text("Login"), button:has-text("Continue")')
        for btn in submit_btns:
            try:
                await btn.click()
                print("Clicked submit for magic code")
                await page.wait_for_timeout(3000)
                break
            except Exception as e:
                print(f"Click failed: {e}")
        
        # Check page for message
        body_text = await page.inner_text('body')
        print(f"After magic code request: {body_text[:2000]}")
        
        # Now check Guerrilla Mail for the magic code
        print("\nChecking Guerrilla Mail for magic code...")
        await page.goto("https://www.guerrillamail.com", wait_until="networkidle")
        await page.wait_for_timeout(5000)
        
        # Look for emails from stacker.news
        emails = await page.query_selector_all('tr, [class*="mail"], [class*="email"], [class*="message"]')
        magic_code = None
        for email in emails[:30]:
            text = await email.inner_text()
            if 'stacker' in text.lower() or 'magic' in text.lower() or 'code' in text.lower() or 'login' in text.lower():
                print(f"Potential email: {text[:300]}")
                # Extract 6-digit code
                codes = re.findall(r'\b\d{6}\b', text)
                if codes:
                    magic_code = codes[0]
                    print(f"Found magic code: {magic_code}")
                    break
        
        if not magic_code:
            # Try to click on the email to open it
            for email in emails[:20]:
                text = await email.inner_text()
                if 'stacker' in text.lower():
                    links = await email.query_selector_all('a')
                    for link in links:
                        href = await link.get_attribute('href')
                        if href:
                            print(f"Opening email link: {href}")
                            try:
                                await page.goto(href, wait_until="networkidle")
                                await page.wait_for_timeout(3000)
                                email_body = await page.inner_text('body')
                                print(f"Email body: {email_body[:2000]}")
                                codes = re.findall(r'\b\d{6}\b', email_body)
                                if codes:
                                    magic_code = codes[0]
                                    print(f"Found magic code: {magic_code}")
                                    break
                            except Exception as e:
                                print(f"Failed to open email: {e}")
                    if magic_code:
                        break
        
        if magic_code:
            print(f"\nUsing magic code: {magic_code}")
            # Go back to Stacker News and enter code
            await page.goto("https://stacker.news/email", wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            # Find code input
            code_inputs = await page.query_selector_all('input[name="code"], input[placeholder*="code" i], input[type="text"]')
            for inp in code_inputs:
                try:
                    await inp.fill(magic_code)
                    print(f"Filled magic code: {magic_code}")
                except Exception as e:
                    print(f"Fill failed: {e}")
            
            # Submit
            submit_btns = await page.query_selector_all('button[type="submit"], button:has-text("Submit"), button:has-text("Verify"), button:has-text("Login")')
            for btn in submit_btns:
                try:
                    await btn.click()
                    print("Submitted magic code")
                    await page.wait_for_timeout(5000)
                    break
                except Exception as e:
                    print(f"Click failed: {e}")
            
            # Check if logged in
            await page.goto("https://stacker.news", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            body_text = await page.inner_text('body')
            print(f"After login: {body_text[:3000]}")
            
            # Check wallet balance
            if 'sat' in body_text.lower() or 'wallet' in body_text.lower() or 'balance' in body_text.lower():
                print("Wallet info found!")
            
            # Try to set username if not set
            # Look for profile/settings
            profile_btns = await page.query_selector_all('a:has-text("Profile"), a:has-text("Settings"), a:has-text("@"), button:has-text("Profile")')
            for btn in profile_btns:
                text = await btn.inner_text()
                print(f"Profile button: {text.strip()}")
                try:
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    profile_text = await page.inner_text('body')
                    print(f"Profile page: {profile_text[:2000]}")
                except Exception as e:
                    print(f"Click failed: {e}")
        else:
            print("No magic code found")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(stacker_news_auth())