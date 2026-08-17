#!/usr/bin/env python3
"""Click Stacker News signup button and complete auth."""
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
        
        # Go to Stacker News
        print("Going to Stacker News...")
        await page.goto("https://stacker.news", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Click signup button (id="signup")
        signup_btn = await page.query_selector('#signup')
        if signup_btn:
            print("Found signup button, clicking...")
            await signup_btn.click()
            await page.wait_for_timeout(3000)
        else:
            print("Signup button not found")
            await browser.close()
            return
        
        # Check for modal
        body_text = await page.inner_text('body')
        print(f"After signup click: {body_text[:3000]}")
        
        # Look for email input in modal
        email_inputs = await page.query_selector_all('input[type="email"], input[name="email"], input[placeholder*="email" i]')
        print(f"Email inputs: {len(email_inputs)}")
        
        # Get temp email
        await page.goto("https://www.guerrillamail.com", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        email_elem = await page.query_selector('#email-widget, #inbox-id, .email-address, #email_addr, input[readonly]')
        temp_email = ""
        if email_elem:
            temp_email = await email_elem.inner_text()
            temp_email = temp_email.strip()
            if not temp_email or '@' not in temp_email:
                temp_email = await email_elem.get_attribute('value')
        print(f"Temp email: {temp_email}")
        
        if not temp_email or '@' not in temp_email:
            print("No valid temp email")
            await browser.close()
            return
        
        # Go back to Stacker News
        await page.goto("https://stacker.news", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        # Click signup again
        signup_btn = await page.query_selector('#signup')
        if signup_btn:
            await signup_btn.click()
            await page.wait_for_timeout(3000)
        
        # Fill email
        email_inputs = await page.query_selector_all('input[type="email"], input[name="email"], input[placeholder*="email" i]')
        for inp in email_inputs:
            try:
                await inp.fill(temp_email)
                print(f"Filled email: {temp_email}")
            except Exception as e:
                print(f"Fill failed: {e}")
        
        # Submit
        submit_btns = await page.query_selector_all('button[type="submit"], button:has-text("Send"), button:has-text("Continue"), button:has-text("Sign up"), button:has-text("Login")')
        for btn in submit_btns:
            try:
                await btn.click()
                print("Clicked submit for magic code")
                await page.wait_for_timeout(3000)
                break
            except Exception as e:
                print(f"Click failed: {e}")
        
        # Check for success message
        body_text = await page.inner_text('body')
        print(f"After submit: {body_text[:2000]}")
        
        # Check Guerrilla Mail for magic code
        print("\nChecking Guerrilla Mail...")
        await page.goto("https://www.guerrillamail.com", wait_until="networkidle")
        await page.wait_for_timeout(5000)
        
        # Refresh
        refresh_btn = await page.query_selector('button:has-text("Refresh"), button:has-text("Check")')
        if refresh_btn:
            await refresh_btn.click()
            await page.wait_for_timeout(3000)
        
        emails = await page.query_selector_all('tr, [class*="mail"], [class*="email"], [class*="message"]')
        magic_code = None
        for email in emails[:30]:
            text = await email.inner_text()
            if 'stacker' in text.lower() or 'magic' in text.lower() or 'code' in text.lower() or 'login' in text.lower() or 'verify' in text.lower():
                print(f"Potential email: {text[:300]}")
                codes = re.findall(r'\b\d{6}\b', text)
                if codes:
                    magic_code = codes[0]
                    print(f"Found magic code: {magic_code}")
                    break
        
        if not magic_code:
            for email in emails[:20]:
                text = await email.inner_text()
                if 'stacker' in text.lower():
                    links = await email.query_selector_all('a')
                    for link in links:
                        href = await link.get_attribute('href')
                        if href:
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
                                print(f"Failed: {e}")
                    if magic_code:
                        break
        
        if magic_code:
            print(f"\nUsing magic code: {magic_code}")
            # Go to email verification page
            await page.goto("https://stacker.news/email", wait_until="networkidle")
            await page.wait_for_timeout(2000)
            
            code_inputs = await page.query_selector_all('input[name="code"], input[placeholder*="code" i], input[type="text"], input[maxlength="6"]')
            for inp in code_inputs:
                try:
                    await inp.fill(magic_code)
                    print(f"Filled magic code: {magic_code}")
                except Exception as e:
                    print(f"Fill failed: {e}")
            
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
            if 'sat' in body_text.lower() or 'wallet' in body_text.lower() or '@' in body_text:
                print("Logged in! Checking wallet...")
                
                # Try to find wallet page
                wallet_links = await page.query_selector_all('a:has-text("Wallet"), a:has-text("wallet"), a[href*="wallet"], a[href*="@"]')
                for link in wallet_links:
                    text = await link.inner_text()
                    href = await link.get_attribute('href')
                    print(f"Wallet link: {text.strip()} -> {href}")
                    if href:
                        await page.goto(href if href.startswith('http') else f"https://stacker.news{href}", wait_until="networkidle")
                        await page.wait_for_timeout(3000)
                        wallet_text = await page.inner_text('body')
                        print(f"Wallet page: {wallet_text[:2000]}")
        else:
            print("No magic code found")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(signup_stacker())