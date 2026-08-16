#!/usr/bin/env python3
"""
Debug script to check Hyper signup flow
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
        
        # Go to Hyper auth page
        await page.goto("https://hyper.charm.land/auth?mode=signup", wait_until="domcontentloaded", timeout=30000)
        print(f"Signup page: {page.url}")
        
        # Fill form with test data
        await page.wait_for_selector('#name', timeout=15000)
        await page.fill('#name', 'Test User')
        await page.fill('#email', 'test@example.com')
        await page.fill('#password', 'testpassword123')
        
        # Handle Turnstile
        try:
            await page.wait_for_selector('.cf-turnstile', timeout=15000)
            await asyncio.sleep(5)
            frames = page.frames
            for frame in frames:
                if 'turnstile' in frame.url or 'challenges.cloudflare' in frame.url:
                    try:
                        await frame.click('input[type="checkbox"]', timeout=5000)
                        print("Clicked Turnstile checkbox")
                        await asyncio.sleep(5)
                        break
                    except:
                        pass
        except:
            pass
        
        # Submit
        await page.click('button[type="submit"]:has-text("Create Account")')
        print("Submitted form")
        
        await page.wait_for_load_state("domcontentloaded", timeout=30000)
        print(f"After submit URL: {page.url}")
        
        # Save content
        content = await page.content()
        with open("/home/user/income-quest/hyper_debug_submit.html", "w") as f:
            f.write(content)
        print(f"Content saved ({len(content)} chars)")
        print(f"First 5000 chars:\n{content[:5000]}")
        
        # Try to go to dashboard
        await page.goto("https://hyper.charm.land/dashboard", wait_until="domcontentloaded", timeout=30000)
        print(f"Dashboard URL: {page.url}")
        content = await page.content()
        with open("/home/user/income-quest/hyper_debug_dashboard.html", "w") as f:
            f.write(content)
        print(f"Dashboard content ({len(content)} chars)")
        print(f"First 5000 chars:\n{content[:5000]}")
        
        # Try signin page
        await page.goto("https://hyper.charm.land/auth?mode=signin", wait_until="domcontentloaded", timeout=30000)
        print(f"Signin URL: {page.url}")
        content = await page.content()
        print(f"Signin content (first 3000):\n{content[:3000]}")
        
        await browser.close()

asyncio.run(main())