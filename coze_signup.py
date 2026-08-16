#!/usr/bin/env python3
"""
Playwright script to sign up for Coze and get a Personal Access Token.
"""
import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def get_coze_pat():
    """Sign up for Coze and retrieve a Personal Access Token."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        
        try:
            print("Navigating to Coze signup...")
            await page.goto("https://www.coze.com", wait_until="networkidle", timeout=60000)
            print(f"Current URL: {page.url}")
            
            # Look for signup button
            signup_selectors = [
                'button:has-text("Sign up")',
                'a:has-text("Sign up")',
                'button:has-text("Sign Up")',
                'a:has-text("Sign Up")',
                '[data-testid="signup"]',
                '.signup-btn',
                '#signup'
            ]
            
            signup_clicked = False
            for selector in signup_selectors:
                try:
                    await page.click(selector, timeout=5000)
                    print(f"Clicked signup with selector: {selector}")
                    signup_clicked = True
                    break
                except:
                    continue
            
            if not signup_clicked:
                # Try to find any clickable element with signup text
                elements = await page.query_selector_all('button, a')
                for el in elements:
                    text = await el.inner_text()
                    if 'sign up' in text.lower() or 'signup' in text.lower():
                        await el.click()
                        print(f"Clicked signup element with text: {text}")
                        signup_clicked = True
                        break
            
            if not signup_clicked:
                print("Could not find signup button, trying direct signup URL")
                await page.goto("https://www.coze.com/signup", wait_until="networkidle", timeout=60000)
            
            print(f"After signup click, URL: {page.url}")
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            # Take screenshot for debugging
            await page.screenshot(path="/tmp/coze_signup.png")
            print("Screenshot saved to /tmp/coze_signup.png")
            
            # Print page content for debugging
            content = await page.content()
            print(f"Page content length: {len(content)}")
            # Print first 5000 chars
            print(content[:5000])
            
        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path="/tmp/coze_error.png")
            print("Error screenshot saved to /tmp/coze_error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(get_coze_pat())