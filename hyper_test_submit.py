#!/usr/bin/env python3
"""
Quick test: Hyper signup with real temp email, save full page content
"""
import asyncio
import sys
sys.path.insert(0, '/home/user/playwright-venv/lib/python3.11/site-packages')
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        # Get temp email
        await page.goto("https://10minutemail.net", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector('#fe_text', timeout=15000)
        email = await page.input_value('#fe_text')
        print(f"Email: {email}")
        
        temp_mail_page = page
        
        # Sign up for Hyper
        hyper_page = await context.new_page()
        await hyper_page.goto("https://hyper.charm.land/auth?mode=signup", wait_until="domcontentloaded", timeout=30000)
        
        await hyper_page.wait_for_selector('#name', timeout=15000)
        await hyper_page.fill('#name', 'Test User')
        await hyper_page.fill('#email', email)
        await hyper_page.fill('#password', 'testpassword123')
        
        # Handle Turnstile - wait longer
        try:
            await hyper_page.wait_for_selector('.cf-turnstile', timeout=15000)
            print("Turnstile found, waiting 15s for auto-complete...")
            await asyncio.sleep(15)
            
            # Check if response token is filled
            token = await hyper_page.evaluate('document.querySelector("input[name=\\"cf-turnstile-response\\"]")?.value')
            print(f"Turnstile token: {token[:50] if token else 'empty'}")
        except:
            pass
        
        # Submit
        await hyper_page.click('button[type="submit"]:has-text("Create Account")')
        print("Submitted")
        
        await hyper_page.wait_for_load_state("domcontentloaded", timeout=30000)
        print(f"After submit URL: {hyper_page.url}")
        
        # Save full content
        content = await hyper_page.content()
        with open("/home/user/income-quest/hyper_full_after_submit.html", "w") as f:
            f.write(content)
        print(f"Full content saved ({len(content)} chars)")
        
        # Search for key phrases
        for phrase in ["verify", "check your email", "confirm", "activation", "success", "error", "internal", "welcome", "dashboard", "account created"]:
            if phrase in content.lower():
                idx = content.lower().index(phrase)
                print(f"Found '{phrase}' at {idx}: ...{content[max(0,idx-100):idx+200]}...")
        
        await browser.close()

asyncio.run(main())