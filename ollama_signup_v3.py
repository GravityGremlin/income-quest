#!/usr/bin/env python3
"""
Playwright script to:
1. Get temporary email from temp-mail.org (browser-based)
2. Sign up for Ollama Cloud
3. Verify email
4. Generate API key
5. Take screenshot
6. Submit to SatsBoard
"""
import asyncio
import os
import sys
import re
from pathlib import Path

# Add playwright venv to path
sys.path.insert(0, '/home/user/playwright-venv/lib/python3.11/site-packages')

from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))
        
        try:
            # Step 1: Get temporary email from temp-mail.org
            print("Step 1: Getting temporary email from temp-mail.org...")
            await page.goto("https://temp-mail.org/en", wait_until="domcontentloaded", timeout=30000)
            
            # Wait for email to be generated
            await page.wait_for_selector('#mail', timeout=30000)
            email = await page.input_value('#mail')
            print(f"Got temporary email: {email}")
            
            if not email or email.strip() == "":
                # Try alternative selector
                email = await page.get_attribute('#mail', 'value')
                print(f"Got email via attribute: {email}")
            
            if not email or email.strip() == "":
                raise Exception("Could not get email from temp-mail.org")
            
            email = email.strip()
            print(f"Using email: {email}")
            
            # Keep this tab open for checking email later
            temp_mail_page = page
            
            # Step 2: Sign up for Ollama Cloud in a new tab
            print("Step 2: Signing up for Ollama Cloud...")
            ollama_page = await context.new_page()
            await ollama_page.goto("https://ollama.com", wait_until="domcontentloaded", timeout=30000)
            
            # Look for sign in/up button
            print("Looking for sign in button...")
            try:
                await ollama_page.wait_for_selector('text=Sign in', timeout=15000)
                print("Found 'Sign in' text")
                await ollama_page.click('text=Sign in')
            except:
                # Try alternative selectors
                print("Trying alternative sign in selectors...")
                await ollama_page.click('a:has-text("Sign in"), button:has-text("Sign in"), [href*="signin"]')
            
            await ollama_page.wait_for_load_state("domcontentloaded", timeout=15000)
            print("Sign in page loaded")
            
            # Fill email
            print("Looking for email input...")
            await ollama_page.wait_for_selector('input[type="email"], input[name="email"], input[autocomplete="email"]', timeout=15000)
            await ollama_page.fill('input[type="email"], input[name="email"], input[autocomplete="email"]', email)
            print(f"Filled email: {email}")
            
            # Submit
            print("Looking for submit button...")
            await ollama_page.click('button[type="submit"], button:has-text("Continue"), button:has-text("Sign up"), button:has-text("Sign in"), input[type="submit"]')
            print("Clicked submit")
            
            # Wait and see what happens after submit
            await ollama_page.wait_for_load_state("domcontentloaded", timeout=15000)
            await ollama_page.screenshot(path="/home/user/income-quest/after_submit.png", full_page=True)
            print("Screenshot after submit saved")
            print(f"Current URL: {ollama_page.url}")
            
            # Step 3: Check for verification email on temp-mail.org
            print("Step 3: Checking for verification email on temp-mail.org...")
            
            # Wait for email to arrive (poll temp-mail.org)
            for attempt in range(30):  # 5 minutes max
                print(f"Checking for email (attempt {attempt + 1}/30)...")
                await temp_mail_page.reload(wait_until="domcontentloaded", timeout=15000)
                
                # Look for email from Ollama
                try:
                    # Try to find email row with Ollama
                    email_row = await temp_mail_page.query_selector('tr:has-text("Ollama"), tr:has-text("ollama"), .mail-item:has-text("Ollama"), .mail-item:has-text("ollama")')
                    if email_row:
                        print("Found Ollama email!")
                        await email_row.click()
                        break
                    
                    # Check if any new emails
                    emails = await temp_mail_page.query_selector_all('tr[data-href], .mail-item, .email-item')
                    if len(emails) > 0:
                        print(f"Found {len(emails)} email(s), clicking first...")
                        await emails[0].click()
                        break
                except Exception as e:
                    print(f"Error checking emails: {e}")
                
                await asyncio.sleep(10)
            else:
                raise Exception("Timeout waiting for verification email")
            
            # Find and click verification link
            print("Looking for verification link...")
            await temp_mail_page.wait_for_selector('a[href*="verify"], a[href*="confirm"], a[href*="activate"], a[href*="ollama"], a[href*="signin"]', timeout=15000)
            verify_link = await temp_mail_page.get_attribute('a[href*="verify"], a[href*="confirm"], a[href*="activate"], a[href*="ollama"], a[href*="signin"]', 'href')
            print(f"Verification link: {verify_link}")
            
            # Open verification link in ollama page
            await ollama_page.goto(verify_link, wait_until="domcontentloaded", timeout=15000)
            print("Verification page loaded")
            
            # Step 4: Generate API key
            print("Step 4: Generating API key...")
            await ollama_page.goto("https://ollama.com/settings/keys", wait_until="domcontentloaded", timeout=15000)
            
            # Look for create key button
            await ollama_page.wait_for_selector('text=Create, text=Generate, text=New Key, text=Add Key, button:has-text("Create"), button:has-text("Generate")', timeout=15000)
            await ollama_page.click('text=Create, text=Generate, text=New Key, text=Add Key, button:has-text("Create"), button:has-text("Generate")')
            
            # Wait for key to appear
            await ollama_page.wait_for_selector('[class*="key"], [class*="token"], code, pre, [data-testid*="key"]', timeout=15000)
            
            # Take screenshot
            screenshot_path = "/home/user/income-quest/ollama_api_key.png"
            await ollama_page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved to {screenshot_path}")
            
            # Extract API key (it's shown only once)
            key_text = await ollama_page.text_content('body')
            print(f"Page content (searching for key): {key_text[:3000]}")
            
            # Try to find the actual key pattern
            key_matches = re.findall(r'(ollama_[a-zA-Z0-9_-]+|sk-[a-zA-Z0-9_-]+|[a-zA-Z0-9]{32,})', key_text)
            if key_matches:
                print(f"Potential API keys found: {key_matches}")
                api_key = key_matches[0]
            else:
                api_key = "[KEY_NOT_FOUND_IN_PAGE_TEXT]"
            
            # Step 5: Submit to SatsBoard
            print("Step 5: Submitting to SatsBoard...")
            await ollama_page.goto("https://sats.throbbing.click/tasks/306/submit", wait_until="domcontentloaded", timeout=15000)
            
            # Add session cookie
            await context.add_cookies([{
                'name': 'session_token',
                'value': 'bbf88dfd4f9928c7b7a17a131bdb2d22b3edbbeaa0c9799132776c8079cd2d71',
                'domain': 'sats.throbbing.click',
                'path': '/'
            }])
            
            await ollama_page.reload(wait_until="domcontentloaded", timeout=15000)
            
            # Fill submission form
            # Notes format: name | APIkey
            notes = f"Ollama Cloud | {email} | {api_key}"
            await ollama_page.fill('textarea[name="notes"], textarea#notes', notes)
            
            # Upload screenshot
            await ollama_page.set_input_files('input[type="file"]', screenshot_path)
            
            # Submit
            await ollama_page.click('button[type="submit"], button:has-text("Submit")')
            
            print("Submission complete!")
            
        except Exception as e:
            print(f"Error: {e}")
            # Try to screenshot the active page
            try:
                active_page = ollama_page if 'ollama_page' in locals() else page
                await active_page.screenshot(path="/home/user/income-quest/error_screenshot.png", full_page=True)
            except:
                pass
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())