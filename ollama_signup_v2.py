#!/usr/bin/env python3
"""
Playwright script to:
1. Create temporary email via mail.tm API
2. Sign up for Ollama Cloud
3. Verify email via mail.tm API
4. Generate API key
5. Take screenshot
6. Submit to SatsBoard
"""
import asyncio
import os
import sys
import re
import requests
import json
from pathlib import Path

# Add playwright venv to path
sys.path.insert(0, '/home/user/playwright-venv/lib/python3.11/site-packages')

from playwright.async_api import async_playwright

MAIL_TM_DOMAIN = "emalupe.com"
MAIL_TM_BASE = "https://api.mail.tm"

def create_temp_email():
    """Create a temporary email account via mail.tm API."""
    email = f"ollama-{int(asyncio.get_event_loop().time() * 1000)}@{MAIL_TM_DOMAIN}"
    password = "temppass123"
    
    # Create account
    resp = requests.post(f"{MAIL_TM_BASE}/accounts", json={"address": email, "password": password}, timeout=30)
    if resp.status_code == 429:
        # Rate limited, try a different approach
        print("Rate limited, waiting...")
        import time
        time.sleep(5)
        resp = requests.post(f"{MAIL_TM_BASE}/accounts", json={"address": email, "password": password}, timeout=30)
    
    if resp.status_code not in (200, 201):
        print(f"Failed to create account: {resp.status_code} - {resp.text}")
        # Try with a different random suffix
        import random
        email = f"ollama-{random.randint(100000, 999999)}@{MAIL_TM_DOMAIN}"
        resp = requests.post(f"{MAIL_TM_BASE}/accounts", json={"address": email, "password": password}, timeout=30)
        if resp.status_code not in (200, 201):
            raise Exception(f"Failed to create email account: {resp.text}")
    
    print(f"Created email account: {email}")
    
    # Get token
    resp = requests.post(f"{MAIL_TM_BASE}/token", json={"address": email, "password": password}, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"Failed to get token: {resp.text}")
    
    token = resp.json()["token"]
    print("Got authentication token")
    return email, token, password

def wait_for_verification_email(token, timeout=180):
    """Wait for and return verification email from Ollama."""
    headers = {"Authorization": f"Bearer {token}"}
    import time
    start = time.time()
    
    while time.time() - start < timeout:
        resp = requests.get(f"{MAIL_TM_BASE}/messages", headers=headers, timeout=30)
        if resp.status_code == 200:
            messages = resp.json().get("hydra:member", [])
            print(f"Checked mail.tm: {len(messages)} messages total")
            for msg in messages:
                subject = msg.get("subject", "")
                from_addr = msg.get("from", {}).get("address", "")
                print(f"  Message: from={from_addr}, subject={subject}")
                if "ollama" in subject.lower() or "ollama" in from_addr.lower() or "sign" in subject.lower() or "magic" in subject.lower() or "verify" in subject.lower():
                    print(f"Found relevant email: {subject}")
                    # Get full message
                    msg_id = msg["id"]
                    resp = requests.get(f"{MAIL_TM_BASE}/messages/{msg_id}", headers=headers, timeout=30)
                    if resp.status_code == 200:
                        full_msg = resp.json()
                        return full_msg
        time.sleep(5)
    
    # Print all messages for debugging
    resp = requests.get(f"{MAIL_TM_BASE}/messages", headers=headers, timeout=30)
    if resp.status_code == 200:
        messages = resp.json().get("hydra:member", [])
        print(f"Final check - all messages ({len(messages)}):")
        for msg in messages:
            print(f"  from={msg.get('from', {}).get('address', '')}, subject={msg.get('subject', '')}")
    
    raise Exception("Timeout waiting for verification email")

def extract_verification_link(email_content):
    """Extract verification link from email content."""
    # Look for links in text or html
    for field in ["text", "html"]:
        content = email_content.get(field, "")
        # Find verification links
        import re
        links = re.findall(r'https?://[^\s<>"\']*(?:verify|confirm|activate|ollama)[^\s<>"\']*', content, re.IGNORECASE)
        if links:
            return links[0]
        # Generic link pattern
        links = re.findall(r'https?://[^\s<>"\']+', content)
        for link in links:
            if "ollama" in link or "verify" in link or "confirm" in link or "activate" in link:
                return link
    return None

async def main():
    # Step 0: Create temporary email via API
    print("Step 0: Creating temporary email via mail.tm API...")
    email, token, password = create_temp_email()
    print(f"Using email: {email}")
    
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
            # Step 1: Sign up for Ollama Cloud
            print("Step 1: Signing up for Ollama Cloud...")
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
            
            # Wait and see what happens after submit
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
            await page.screenshot(path="/home/user/income-quest/after_submit.png", full_page=True)
            print("Screenshot after submit saved")
            print(f"Current URL: {page.url}")
            
            # Step 2: Wait for verification email via API
            print("Step 2: Waiting for verification email via mail.tm API...")
            email_data = wait_for_verification_email(token)
            
            # Extract verification link
            verify_link = extract_verification_link(email_data)
            if not verify_link:
                print("Could not find verification link in email")
                print(f"Email content: {json.dumps(email_data, indent=2)[:2000]}")
                raise Exception("No verification link found")
            
            print(f"Verification link: {verify_link}")
            
            # Click verification link
            await page.goto(verify_link, wait_until="domcontentloaded", timeout=15000)
            print("Verification page loaded")
            
            # Step 3: Generate API key
            print("Step 3: Generating API key...")
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
                api_key = key_matches[0]
            else:
                api_key = "[KEY_NOT_FOUND_IN_PAGE_TEXT]"
            
            # Step 4: Submit to SatsBoard
            print("Step 4: Submitting to SatsBoard...")
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
            notes = f"Ollama Cloud | {email} | {api_key}"
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