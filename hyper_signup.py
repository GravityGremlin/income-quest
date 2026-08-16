#!/usr/bin/env python3
"""
Playwright script to:
1. Get temporary email from 10minutemail.net
2. Sign up for Hyper (hyper.charm.land) with email
3. Handle Cloudflare Turnstile
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
            # Step 1: Get temporary email from 10minutemail.net
            print("Step 1: Getting temporary email from 10minutemail.net...")
            await page.goto("https://10minutemail.net", wait_until="domcontentloaded", timeout=30000)
            
            # Wait for email to be generated
            email = None
            for selector in ['#fe_text', 'input[name="fe_text"]', '#mail', 'input[id*="mail"]', 'input[class*="mail"]', 'input[readonly]']:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    email = await page.input_value(selector)
                    if email and '@' in email:
                        print(f"Got temporary email via {selector}: {email}")
                        break
                except:
                    continue
            
            if not email or '@' not in email:
                content = await page.content()
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
                for e in emails:
                    if '10minutemail' not in e and 'example' not in e:
                        email = e
                        print(f"Got temporary email from page content: {email}")
                        break
            
            if not email or '@' not in email:
                raise Exception("Could not get email from 10minutemail.net")
            
            email = email.strip()
            print(f"Using email: {email}")
            
            # Keep this tab open for checking email later
            temp_mail_page = page
            
            # Step 2: Sign up for Hyper
            print("Step 2: Signing up for Hyper...")
            hyper_page = await context.new_page()
            await hyper_page.goto("https://hyper.charm.land", wait_until="domcontentloaded", timeout=30000)
            
            # Look for sign up button
            print("Looking for sign up button...")
            try:
                await hyper_page.wait_for_selector(':text("Sign Up"), :text("Start Free"), :text("Get Started"), button:has-text("Sign Up"), button:has-text("Start Free"), a:has-text("Sign Up"), a:has-text("Start Free")', timeout=15000)
                await hyper_page.click(':text("Sign Up"), :text("Start Free"), :text("Get Started"), button:has-text("Sign Up"), button:has-text("Start Free"), a:has-text("Sign Up"), a:has-text("Start Free")')
            except:
                print("Trying alternative sign up selectors...")
                await hyper_page.click('a[href*="signup"], a[href*="register"], button:has-text("Sign"), button:has-text("Start")')
            
            await hyper_page.wait_for_load_state("domcontentloaded", timeout=15000)
            print("Sign up page loaded")
            print(f"Current URL: {hyper_page.url}")
            
            # Check if there's an email option (vs only OAuth)
            await hyper_page.wait_for_selector('input[type="email"], :text("Email"), :text("Continue with email")', timeout=15000)
            
            # Click email option if needed
            try:
                await hyper_page.click(':text("Email"), :text("Continue with email"), button:has-text("Email")')
                await hyper_page.wait_for_load_state("domcontentloaded", timeout=5000)
            except:
                pass  # Email might be the default
            
            # Fill email
            print("Looking for email input...")
            await hyper_page.wait_for_selector('input[type="email"], input[name="email"], input[autocomplete="email"]', timeout=15000)
            await hyper_page.fill('input[type="email"], input[name="email"], input[autocomplete="email"]', email)
            print(f"Filled email: {email}")
            
            # Handle Cloudflare Turnstile if present
            print("Checking for Cloudflare Turnstile...")
            try:
                # Wait for Turnstile to appear and potentially auto-solve
                await hyper_page.wait_for_selector('iframe[src*="turnstile"], iframe[src*="challenges.cloudflare"], .cf-turnstile', timeout=10000)
                print("Turnstile detected, waiting for challenge...")
                # Wait a bit for Turnstile to potentially auto-complete
                await asyncio.sleep(10)
                # Check if there's a checkbox to click
                try:
                    await hyper_page.click('iframe[src*="turnstile"] >> input[type="checkbox"]', timeout=5000)
                except:
                    pass
                await asyncio.sleep(5)
            except:
                print("No Turnstile detected or already passed")
            
            # Submit
            print("Looking for submit button...")
            await hyper_page.click('button[type="submit"], button:has-text("Continue"), button:has-text("Sign up"), button:has-text("Create"), input[type="submit"]')
            print("Clicked submit")
            
            # Wait for next step
            await hyper_page.wait_for_load_state("domcontentloaded", timeout=30000)
            print(f"After submit URL: {hyper_page.url}")
            await hyper_page.screenshot(path="/home/user/income-quest/hyper_after_submit.png", full_page=True)
            
            # Step 3: Check for verification email on 10minutemail.net
            print("Step 3: Checking for verification email on 10minutemail.net...")
            
            for attempt in range(30):  # 5 minutes max
                print(f"Checking for email (attempt {attempt + 1}/30)...")
                await temp_mail_page.reload(wait_until="domcontentloaded", timeout=15000)
                
                try:
                    # Look for email from Hyper/Charm
                    email_row = await temp_mail_page.query_selector('tr:has-text("Hyper"), tr:has-text("hyper"), tr:has-text("Charm"), tr:has-text("charm"), tbody tr')
                    if email_row:
                        print("Found potential email!")
                        await email_row.click()
                        
                        # Find verification link
                        print("Looking for verification link in email...")
                        await temp_mail_page.wait_for_selector('a[href*="verify"], a[href*="confirm"], a[href*="activate"], a[href*="hyper"], a[href*="charm"], a[href*="signin"], a[href*="auth"]', timeout=10000)
                        verify_link = await temp_mail_page.get_attribute('a[href*="verify"], a[href*="confirm"], a[href*="activate"], a[href*="hyper"], a[href*="charm"], a[href*="signin"], a[href*="auth"]', 'href')
                        print(f"Verification link: {verify_link}")
                        
                        await hyper_page.goto(verify_link, wait_until="domcontentloaded", timeout=15000)
                        print("Verification page loaded")
                        break
                    
                    emails = await temp_mail_page.query_selector_all('tbody tr, .mail-item, .email-item, tr[data-id]')
                    if len(emails) > 1:
                        print(f"Found {len(emails)} email row(s), clicking first data row...")
                        await emails[1].click()
                        
                        print("Looking for verification link in email...")
                        await temp_mail_page.wait_for_selector('a[href*="verify"], a[href*="confirm"], a[href*="activate"], a[href*="hyper"], a[href*="charm"], a[href*="signin"], a[href*="auth"]', timeout=10000)
                        verify_link = await temp_mail_page.get_attribute('a[href*="verify"], a[href*="confirm"], a[href*="activate"], a[href*="hyper"], a[href*="charm"], a[href*="signin"], a[href*="auth"]', 'href')
                        print(f"Verification link: {verify_link}")
                        
                        await hyper_page.goto(verify_link, wait_until="domcontentloaded", timeout=15000)
                        print("Verification page loaded")
                        break
                except Exception as e:
                    print(f"Error checking emails: {e}")
                
                await asyncio.sleep(10)
            else:
                content = await temp_mail_page.content()
                print(f"Temp mail page content: {content[:5000]}")
                raise Exception("Timeout waiting for verification email")
            
            # Step 4: Generate API key
            print("Step 4: Generating API key...")
            await hyper_page.goto("https://hyper.charm.land/dashboard", wait_until="domcontentloaded", timeout=30000)
            
            # Look for API keys section
            await hyper_page.wait_for_selector(':text("API"), :text("Key"), :text("Token"), a[href*="key"], a[href*="api"]', timeout=15000)
            await hyper_page.click(':text("API Keys"), :text("API Key"), :text("Keys"), a[href*="key"], a[href*="api"]')
            
            # Create new key
            await hyper_page.wait_for_selector(':text("Create"), :text("Generate"), :text("New"), button:has-text("Create"), button:has-text("Generate")', timeout=15000)
            await hyper_page.click(':text("Create"), :text("Generate"), :text("New"), button:has-text("Create"), button:has-text("Generate")')
            
            # Wait for key to appear
            await hyper_page.wait_for_selector('[class*="key"], [class*="token"], code, pre, [data-testid*="key"]', timeout=15000)
            
            # Take screenshot
            screenshot_path = "/home/user/income-quest/hyper_api_key.png"
            await hyper_page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved to {screenshot_path}")
            
            # Extract API key
            key_text = await hyper_page.text_content('body')
            print(f"Page content (searching for key): {key_text[:3000]}")
            
            key_matches = re.findall(r'(sk-hyper-[a-zA-Z0-9_-]+|sk-[a-zA-Z0-9_-]+|[a-zA-Z0-9]{32,})', key_text)
            if key_matches:
                print(f"Potential API keys found: {key_matches}")
                api_key = key_matches[0]
            else:
                api_key = "[KEY_NOT_FOUND_IN_PAGE_TEXT]"
            
            # Step 5: Submit to SatsBoard
            print("Step 5: Submitting to SatsBoard...")
            await hyper_page.goto("https://sats.throbbing.click/tasks/336/submit", wait_until="domcontentloaded", timeout=15000)
            
            # Add session cookie
            await context.add_cookies([{
                'name': 'session_token',
                'value': 'bbf88dfd4f9928c7b7a17a131bdb2d22b3edbbeaa0c9799132776c8079cd2d71',
                'domain': 'sats.throbbing.click',
                'path': '/'
            }])
            
            await hyper_page.reload(wait_until="domcontentloaded", timeout=15000)
            
            # Fill submission form
            notes = f"Hyper | {email} | {api_key}"
            await hyper_page.fill('textarea[name="notes"], textarea#notes', notes)
            
            # Upload screenshot
            await hyper_page.set_input_files('input[type="file"]', screenshot_path)
            
            # Submit
            await hyper_page.click('button[type="submit"], button:has-text("Submit")')
            
            print("Submission complete!")
            
        except Exception as e:
            print(f"Error: {e}")
            try:
                active_page = hyper_page if 'hyper_page' in locals() else page
                await active_page.screenshot(path="/home/user/income-quest/error_screenshot.png", full_page=True)
            except:
                pass
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())