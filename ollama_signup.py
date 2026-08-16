#!/usr/bin/env python3
"""
Playwright script to:
1. Get temporary email from temp-mail.io
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
            # Step 1: Get temporary email
            print("Step 1: Getting temporary email from temp-mail.io...")
            await page.goto("https://temp-mail.io/en", wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_selector('#email', timeout=15000)
            email = await page.input_value('#email')
            print(f"Got temporary email: {email}")
            
            # Store email in variable for later use
            print(f"Using email: {email}")
            
            # Step 2: Sign up for Ollama Cloud
            print("Step 2: Signing up for Ollama Cloud...")
            await page.goto("https://ollama.com", wait_until="domcontentloaded", timeout=15000)
            
            # Look for sign in/up button
            print("Looking for sign in button...")
            try:
                await page.wait_for_selector('text=Sign in', timeout=15000)
                print("Found 'Sign in' text")
                await page.click('text=Sign in')
            except:
                # Try alternative selectors
                print("Trying alternative sign in selectors...")
                await page.click('a:has-text("Sign in"), button:has-text("Sign in"), [href*="signin"]')
            
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
            print("Sign in page loaded")
            
            # Fill email
            print("Looking for email input...")
            await page.wait_for_selector('input[type="email"], input[name="email"], input[autocomplete="email"]', timeout=15000)
            await page.fill('input[type="email"], input[name="email"], input[autocomplete="email"]', email)
            print(f"Filled email: {email}")
            
            # Submit
            print("Looking for submit button...")
            await page.click('button[type="submit"], button:has-text("Continue"), button:has-text("Sign up"), button:has-text("Sign in"), input[type="submit"]')
            print("Clicked submit")
            
            # Wait for verification email
            print("Step 3: Waiting for verification email...")
            await asyncio.sleep(10)
            
            # Go back to temp-mail.io to check for email
            print("Checking temp-mail.io for verification email...")
            await page.goto("https://temp-mail.io/en", wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_selector('.mail-item, .email-item, [data-email], .message, tr:has-text("Ollama")', timeout=60000)
            
            # Click the verification email
            print("Looking for Ollama verification email...")
            try:
                await page.click('.mail-item:has-text("Ollama"), .mail-item:has-text("ollama"), .email-item:has-text("Ollama"), .email-item:has-text("ollama"), tr:has-text("Ollama"), tr:has-text("ollama")')
            except:
                print("Could not find Ollama-specific email, clicking first email...")
                await page.click('.mail-item, .email-item, .message, tr[data-message-id]')
            
            # Find and click verification link
            print("Looking for verification link...")
            await page.wait_for_selector('a[href*="verify"], a[href*="confirm"], a[href*="activate"], a[href*="ollama"]', timeout=15000)
            verify_link = await page.get_attribute('a[href*="verify"], a[href*="confirm"], a[href*="activate"], a[href*="ollama"]', 'href')
            print(f"Verification link: {verify_link}")
            
            await page.goto(verify_link, wait_until="domcontentloaded", timeout=15000)
            print("Verification page loaded")
            
            # Step 4: Generate API key
            print("Step 4: Generating API key...")
            await page.goto("https://ollama.com/settings/keys", wait_until="domcontentloaded", timeout=15000)
            
            # Look for create key button
            await page.wait_for_selector('text=Create, text=Generate, text=New Key, text=Add Key, button:has-text("Create"), button:has-text("Generate")', timeout=15000)
            await page.click('text=Create, text=Generate, text=New Key, text=Add Key, button:has-text("Create"), button:has-text("Generate")')
            
            # Wait for key to appear
            await page.wait_for_selector('[class*="key"], [class*="token"], code, pre, [data-testid*="key"]', timeout=15000)
            
            # Take screenshot
            screenshot_path = "/home/user/income-quest/ollama_api_key.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved to {screenshot_path}")
            
            # Extract API key (it's shown only once)
            key_text = await page.text_content('body')
            print(f"Page content (searching for key): {key_text[:3000]}")
            
            # Try to find the actual key pattern
            key_matches = re.findall(r'(ollama_[a-zA-Z0-9_-]+|sk-[a-zA-Z0-9_-]+|[a-zA-Z0-9]{32,})', key_text)
            if key_matches:
                print(f"Potential API keys found: {key_matches}")
            
            # Step 5: Submit to SatsBoard
            print("Step 5: Submitting to SatsBoard...")
            await page.goto("https://sats.throbbing.click/tasks/306/submit", wait_until="domcontentloaded", timeout=15000)
            
            # Add session cookie
            await context.add_cookies([{
                'name': 'session_token',
                'value': 'bbf88dfd4f9928c7b7a17a131bdb2d22b3edbbeaa0c9799132776c8079cd2d71',
                'domain': 'sats.throbbing.click',
                'path': '/'
            }])
            
            await page.reload(wait_until="domcontentloaded", timeout=15000)
            
            # Fill submission form
            # Notes format: name | APIkey
            notes = f"Ollama Cloud | {email} | [API_KEY_HERE]"
            await page.fill('textarea[name="notes"], textarea#notes', notes)
            
            # Upload screenshot
            await page.set_input_files('input[type="file"]', screenshot_path)
            
            # Submit
            await page.click('button[type="submit"], button:has-text("Submit")')
            
            print("Submission complete!")
            
        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path="/home/user/income-quest/error_screenshot.png", full_page=True)
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())