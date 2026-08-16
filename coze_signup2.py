#!/usr/bin/env python3
"""
Playwright script to complete Coze signup and get PAT.
"""
import asyncio
import os
import tempfile
from playwright.async_api import async_playwright

# Use a temporary email for signup
import random
import string

def generate_email():
    """Generate a random email for signup."""
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    return f"{username}@gmail.com"

async def complete_coze_signup():
    email = generate_email()
    password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%', k=16))
    
    print(f"Using email: {email}")
    print(f"Using password: {password}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
        )
        page = await context.new_page()
        
        try:
            print("Navigating to Coze...")
            await page.goto("https://www.coze.com", wait_until="networkidle", timeout=60000)
            print(f"URL: {page.url}")
            
            # Click "Get started"
            print("Clicking 'Get started'...")
            await page.click('button:has-text("Get started")', timeout=10000)
            await page.wait_for_load_state("networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
            
            print(f"After click, URL: {page.url}")
            
            # Take screenshot
            await page.screenshot(path="/tmp/coze_after_getstarted.png", full_page=True)
            
            # Look for signup form elements
            print("\n=== Looking for signup form ===")
            # Try to find email input
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[placeholder*="email" i]',
                'input[placeholder*="Email" i]',
                '#email',
                '[data-testid="email"]'
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = await page.wait_for_selector(selector, timeout=5000)
                    if email_input:
                        print(f"Found email input with selector: {selector}")
                        break
                except:
                    continue
            
            if not email_input:
                # Print all inputs
                inputs = await page.query_selector_all('input')
                for inp in inputs:
                    type_attr = await inp.get_attribute('type')
                    name_attr = await inp.get_attribute('name')
                    placeholder = await inp.get_attribute('placeholder')
                    print(f"  Input: type={type_attr}, name={name_attr}, placeholder={placeholder}")
                
                # Also check for OAuth buttons
                print("\n=== OAuth buttons ===")
                buttons = await page.query_selector_all('button')
                for btn in buttons:
                    text = await btn.inner_text()
                    if text.strip():
                        print(f"  Button: '{text.strip()}'")
            
            # Check page content
            content = await page.content()
            print(f"\nPage content length: {len(content)}")
            # Save for analysis
            with open("/tmp/coze_signup_page.html", "w") as f:
                f.write(content)
            print("Page HTML saved to /tmp/coze_signup_page.html")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path="/tmp/coze_error.png", full_page=True)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(complete_coze_signup())