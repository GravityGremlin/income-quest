#!/usr/bin/env python3
"""Sign up for Publish0x using Guerrilla Mail."""
import asyncio
from playwright.async_api import async_playwright

async def signup_publish0x():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Get temp email from Guerrilla Mail
        print("Getting temp email from Guerrilla Mail...")
        await page.goto("https://www.guerrillamail.com", wait_until="networkidle")
        await page.wait_for_timeout(5000)
        
        # Try to find email address
        email_selectors = ['#email-widget', '#inbox-id', '.email-address', '#email_addr', '[id*="email"]', 'input[readonly]']
        temp_email = ""
        for selector in email_selectors:
            email_elem = await page.query_selector(selector)
            if email_elem:
                temp_email = await email_elem.inner_text()
                temp_email = temp_email.strip()
                if temp_email and '@' in temp_email:
                    break
                temp_email = await email_elem.get_attribute('value')
                if temp_email and '@' in temp_email:
                    break
        
        print(f"Temp email: {temp_email}")
        
        if not temp_email or '@' not in temp_email:
            # Try sharklasers.com (Guerrilla Mail alias)
            await page.goto("https://sharklasers.com", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            email_elem = await page.query_selector('#email-widget, #inbox-id, .email-address, #email_addr, input[readonly]')
            if email_elem:
                temp_email = await email_elem.inner_text()
                temp_email = temp_email.strip()
                if not temp_email or '@' not in temp_email:
                    temp_email = await email_elem.get_attribute('value')
            print(f"Temp email (sharklasers): {temp_email}")
        
        if not temp_email or '@' not in temp_email:
            print("Could not get valid temp email")
            await browser.close()
            return
        
        # Go to Publish0x and sign up
        print(f"\nNavigating to Publish0x with email: {temp_email}")
        await page.goto("https://www.publish0x.com", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Click "Sign Up & Earn Crypto"
        signup_btn = await page.query_selector('a:has-text("Sign Up"), button:has-text("Sign Up"), a:has-text("Sign Up & Earn")')
        if signup_btn:
            await signup_btn.click()
            await page.wait_for_timeout(3000)
            print("Clicked Sign Up")
        
        body_text = await page.inner_text('body')
        print(f"After signup click: {body_text[:3000]}")
        
        # Fill registration form
        email_inputs = await page.query_selector_all('input[type="email"], input[name*="email"]')
        print(f"Email inputs: {len(email_inputs)}")
        for inp in email_inputs:
            try:
                await inp.fill(temp_email)
                print(f"Filled email: {temp_email}")
            except Exception as e:
                print(f"Fill failed: {e}")
        
        # Username
        username_inputs = await page.query_selector_all('input[name*="user"], input[placeholder*="user" i], input[placeholder*="name" i], input[name="username"]')
        print(f"Username inputs: {len(username_inputs)}")
        for inp in username_inputs:
            try:
                await inp.fill("gravityquest")
                print("Filled username")
            except Exception as e:
                print(f"Fill failed: {e}")
        
        # Password
        pwd_inputs = await page.query_selector_all('input[type="password"]')
        print(f"Password inputs: {len(pwd_inputs)}")
        for inp in pwd_inputs:
            try:
                await inp.fill("TestPass123!")
                print("Filled password")
            except Exception as e:
                print(f"Fill failed: {e}")
        
        # Submit
        submit_btns = await page.query_selector_all('button[type="submit"], button:has-text("Sign Up"), button:has-text("Register"), button:has-text("Create"), input[type="submit"]')
        print(f"Submit buttons: {len(submit_btns)}")
        for btn in submit_btns:
            try:
                await btn.click()
                print("Clicked submit")
                await page.wait_for_timeout(5000)
                break
            except Exception as e:
                print(f"Click failed: {e}")
        
        # Check result
        body_text = await page.inner_text('body')
        print(f"After submit: {body_text[:3000]}")
        
        # Check temp email for verification
        print("\nChecking temp email for verification...")
        await page.goto("https://www.guerrillamail.com", wait_until="networkidle")
        await page.wait_for_timeout(5000)
        
        # Look for emails
        emails = await page.query_selector_all('tr, [class*="mail"], [class*="email"], [class*="message"]')
        for email in emails[:30]:
            text = await email.inner_text()
            if 'publish' in text.lower() or 'verify' in text.lower() or 'confirm' in text.lower() or 'activation' in text.lower():
                print(f"Verification email found: {text[:300]}")
                # Try to click any link in it
                links = await email.query_selector_all('a')
                for link in links:
                    href = await link.get_attribute('href')
                    if href:
                        print(f"Link in email: {href}")
                        try:
                            await page.goto(href, wait_until="networkidle")
                            await page.wait_for_timeout(3000)
                            verify_text = await page.inner_text('body')
                            print(f"Verification result: {verify_text[:2000]}")
                        except Exception as e:
                            print(f"Verification navigation failed: {e}")
                        break
        
        # Go back to Publish0x and check if logged in
        await page.goto("https://www.publish0x.com", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        body_text = await page.inner_text('body')
        print(f"Back to Publish0x: {body_text[:3000]}")
        
        # Look for earning opportunities - tip buttons, balance, etc.
        tip_btns = await page.query_selector_all('button:has-text("Tip"), a:has-text("Tip"), button:has-text("Earn"), a:has-text("Earn")')
        for btn in tip_btns[:10]:
            text = await btn.inner_text()
            print(f"Earning action: {text.strip()}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(signup_publish0x())