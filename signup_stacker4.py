#!/usr/bin/env python3
"""Complete Stacker News signup - wait for magic code."""
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
        
        # Click "Continue with Email"
        email_btn = await page.query_selector('button:has-text("Continue with Email"), a:has-text("Continue with Email")')
        if email_btn:
            await email_btn.click()
            await page.wait_for_timeout(2000)
            print("Clicked Continue with Email")
        
        # Fill email
        email_inputs = await page.query_selector_all('input[type="email"], input[name="email"], input[placeholder*="email" i]')
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
        
        # Wait and check Guerrilla Mail for magic code (poll for up to 60 seconds)
        print("\nPolling Guerrilla Mail for magic code...")
        magic_code = None
        for attempt in range(12):  # 12 attempts * 5 seconds = 60 seconds
            await page.goto("https://www.guerrillamail.com", wait_until="networkidle")
            await page.wait_for_timeout(5000)
            
            # Refresh
            refresh_btn = await page.query_selector('button:has-text("Refresh"), button:has-text("Check")')
            if refresh_btn:
                await refresh_btn.click()
                await page.wait_for_timeout(3000)
            
            body_text = await page.inner_text('body')
            
            # Look for stacker email
            if 'stacker' in body_text.lower() or 'magic' in body_text.lower() or 'code' in body_text.lower() or 'verify' in body_text.lower():
                print(f"Attempt {attempt+1}: Found stacker/magic/code in inbox!")
                codes = re.findall(r'\b\d{6}\b', body_text)
                if codes:
                    magic_code = codes[0]
                    print(f"Found magic code: {magic_code}")
                    break
                
                # Try clicking on email rows
                email_rows = await page.query_selector_all('tr, [class*="mail"], [class*="email"], [class*="message"]')
                for row in email_rows[:20]:
                    text = await row.inner_text()
                    if 'stacker' in text.lower() or 'magic' in text.lower():
                        links = await row.query_selector_all('a')
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
                    break
            else:
                print(f"Attempt {attempt+1}: No stacker email yet, waiting...")
            
            await asyncio.sleep(5)
        
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
            
            submit_btns = await page.query_selector_all('button[type="submit"], button:has-text("Submit"), button:has-text("Verify"), button:has-text("Login"), button:has-text("Continue")')
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
            
            # Check wallet
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
            print("No magic code found after 60 seconds")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(signup_stacker())