#!/usr/bin/env python3
"""Try to register on Microlancer.io using temp email."""
import asyncio
from playwright.async_api import async_playwright

async def register_microlancer():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # First, get a temp email
        print("Getting temp email...")
        await page.goto("https://www.guerrillamail.com", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        email_elem = await page.query_selector('#email-widget, #inbox-id, .email-address, [id*="email"]')
        temp_email = ""
        if email_elem:
            temp_email = await email_elem.inner_text()
            temp_email = temp_email.strip()
        print(f"Temp email: {temp_email}")
        
        if not temp_email:
            # Try another temp email service
            await page.goto("https://temp-mail.org", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            email_elem = await page.query_selector('#mail, .email-address, [id*="email"], #email')
            if email_elem:
                temp_email = await email_elem.inner_text()
                temp_email = temp_email.strip()
            print(f"Temp email (temp-mail.org): {temp_email}")
        
        if not temp_email:
            print("Could not get temp email")
            await browser.close()
            return
        
        # Now go to Microlancer and try to register
        print(f"\nNavigating to Microlancer with email: {temp_email}")
        await page.goto("https://microlancer.io", wait_until="networkidle")
        await page.wait_for_timeout(5000)
        
        # Look for signup/register button
        signup_selectors = [
            'a:has-text("Sign up")',
            'button:has-text("Sign up")',
            'a:has-text("Register")',
            'button:has-text("Register")',
            'a:has-text("Get Started")',
            'button:has-text("Get Started")',
            'a[href*="register"]',
            'a[href*="signup"]',
            'a[href*="sign-up"]',
        ]
        
        clicked = False
        for selector in signup_selectors:
            try:
                elem = await page.query_selector(selector)
                if elem:
                    await elem.click()
                    await page.wait_for_timeout(3000)
                    print(f"Clicked signup via: {selector}")
                    clicked = True
                    break
            except Exception as e:
                print(f"Selector {selector} failed: {e}")
        
        if not clicked:
            print("Could not find signup button, checking page content...")
            body_text = await page.inner_text('body')
            print(f"Body: {body_text[:2000]}")
        
        # Check for registration form
        await page.wait_for_timeout(3000)
        body_text = await page.inner_text('body')
        print(f"After signup click: {body_text[:3000]}")
        
        # Look for email input
        email_inputs = await page.query_selector_all('input[type="email"], input[name*="email"], input[placeholder*="email" i]')
        print(f"Email inputs found: {len(email_inputs)}")
        
        for inp in email_inputs:
            try:
                await inp.fill(temp_email)
                print(f"Filled email: {temp_email}")
            except Exception as e:
                print(f"Fill failed: {e}")
        
        # Look for password input
        pwd_inputs = await page.query_selector_all('input[type="password"], input[name*="password"]')
        print(f"Password inputs found: {len(pwd_inputs)}")
        
        for inp in pwd_inputs:
            try:
                await inp.fill("TestPass123!")
                print("Filled password")
            except Exception as e:
                print(f"Fill failed: {e}")
        
        # Look for submit button
        submit_btns = await page.query_selector_all('button[type="submit"], button:has-text("Register"), button:has-text("Sign up"), button:has-text("Create"), input[type="submit"]')
        print(f"Submit buttons found: {len(submit_btns)}")
        
        for btn in submit_btns:
            try:
                await btn.click()
                print("Clicked submit")
                await page.wait_for_timeout(5000)
                break
            except Exception as e:
                print(f"Click failed: {e}")
        
        # Check result
        final_text = await page.inner_text('body')
        print(f"Final page text: {final_text[:3000]}")
        
        # Check temp email for verification
        print("\nChecking temp email for verification...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(register_microlancer())