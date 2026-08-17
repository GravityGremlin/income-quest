#!/usr/bin/env python3
"""Complete Stacker News signup - extract email from page text."""
import asyncio
import re
from playwright.async_api import async_playwright

async def signup_stacker():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # First get temp email from page text
        print("Getting temp email...")
        await page.goto("https://www.guerrillamail.com", wait_until="networkidle")
        await page.wait_for_timeout(5000)
        
        body_text = await page.inner_text('body')
        # Extract email from page text
        emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', body_text)
        temp_email = None
        for email in emails:
            if 'sharklasers' in email or 'guerrillamail' in email or 'grr.la' in email:
                temp_email = email
                break
        
        if not temp_email and emails:
            temp_email = emails[0]
        
        print(f"Temp email: {temp_email}")
        
        if not temp_email:
            print("Could not get temp email")
            await browser.close()
            return
        
        # Go to Stacker News signup
        print(f"\nGoing to Stacker News signup with: {temp_email}")
        await page.goto("https://stacker.news/signup", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        body_text = await page.inner_text('body')
        print(f"Signup page: {body_text[:2000]}")
        
        # Click "Continue with Email"
        email_btn = await page.query_selector('button:has-text("Continue with Email"), a:has-text("Continue with Email")')
        if email_btn:
            await email_btn.click()
            await page.wait_for_timeout(2000)
            print("Clicked Continue with Email")
        
        # Fill email
        email_inputs = await page.query_selector_all('input[type="email"], input[name="email"], input[placeholder*="email" i]')
        print(f"Email inputs: {len(email_inputs)}")
        for inp in email_inputs:
            try:
                await inp.fill(temp_email)
                print(f"Filled email: {temp_email}")
            except Exception as e:
                print(f"Fill failed: {e}")
        
        # Submit
        submit_btns = await page.query_selector_all('button[type="submit"], button:has-text("Send"), button:has-text("Continue"), button:has-text("Sign up")')
        for btn in submit_btns:
            try:
                await btn.click()
                print("Clicked submit for magic code")
                await page.wait_for_timeout(3000)
                break
            except Exception as e:
                print(f"Click failed: {e}")
        
        # Check for success
        body_text = await page.inner_text('body')
        print(f"After submit: {body_text[:2000]}")
        
        # Check Guerrilla Mail for magic code
        print("\nChecking Guerrilla Mail for magic code...")
        await page.goto("https://www.guerrillamail.com", wait_until="networkidle")
        await page.wait_for_timeout(5000)
        
        # Refresh
        refresh_btn = await page.query_selector('button:has-text("Refresh"), button:has-text("Check")')
        if refresh_btn:
            await refresh_btn.click()
            await page.wait_for_timeout(3000)
        
        body_text = await page.inner_text('body')
        print(f"Inbox page: {body_text[:3000]}")
        
        # Look for stacker email
        emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', body_text)
        print(f"Emails in inbox: {emails[:10]}")
        
        # Search for stacker-related content
        if 'stacker' in body_text.lower() or 'magic' in body_text.lower() or 'code' in body_text.lower():
            print("Found stacker/magic/code in inbox!")
            codes = re.findall(r'\b\d{6}\b', body_text)
            if codes:
                magic_code = codes[0]
                print(f"Found magic code: {magic_code}")
            else:
                print("No 6-digit code found")
        else:
            print("No stacker email visible in inbox text")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(signup_stacker())