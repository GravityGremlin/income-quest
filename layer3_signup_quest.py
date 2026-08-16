#!/usr/bin/env python3
"""Sign up for Layer3 and complete a free Learn quest."""
import asyncio
from playwright.async_api import async_playwright

async def signup_and_quest():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        print("🔍 Navigating to Layer3.xyz...")
        await page.goto("https://layer3.xyz", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Click "Sign up" 
        signup_btn = await page.query_selector('button:has-text("Sign up"), a:has-text("Sign up")')
        if signup_btn:
            await signup_btn.click()
            await page.wait_for_timeout(3000)
            print("Clicked Sign up")
        
        body_text = await page.inner_text('body')
        print(f"After Sign up click: {body_text[:3000]}")
        
        # Look for wallet creation options
        wallet_options = await page.query_selector_all('button:has-text("Layer3 Wallet"), button:has-text("Create"), button:has-text("Continue"), button:has-text("Get Started")')
        for btn in wallet_options:
            text = await btn.inner_text()
            print(f"Wallet option: {text.strip()}")
            try:
                await btn.click()
                await page.wait_for_timeout(3000)
                print(f"Clicked: {text.strip()}")
                break
            except Exception as e:
                print(f"Click failed: {e}")
        
        # Check for email/password or wallet creation flow
        await page.wait_for_timeout(3000)
        body_text = await page.inner_text('body')
        print(f"After wallet option: {body_text[:3000]}")
        
        # Look for email input (if they ask for email)
        email_inputs = await page.query_selector_all('input[type="email"], input[name*="email"]')
        if email_inputs:
            print("Found email input - need temp email")
            # Get temp email
            await page.goto("https://temp-mail.org", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            email_elem = await page.query_selector('#mail, .email-address, [id*="email"], #email')
            temp_email = ""
            if email_elem:
                temp_email = await email_elem.inner_text()
                temp_email = temp_email.strip()
            print(f"Temp email: {temp_email}")
            
            if temp_email:
                await page.goto("https://layer3.xyz", wait_until="networkidle")
                await page.wait_for_timeout(3000)
                # Re-navigate to signup
                signup_btn = await page.query_selector('button:has-text("Sign up"), a:has-text("Sign up")')
                if signup_btn:
                    await signup_btn.click()
                    await page.wait_for_timeout(3000)
                
                wallet_options = await page.query_selector_all('button:has-text("Layer3 Wallet"), button:has-text("Create"), button:has-text("Continue")')
                for btn in wallet_options:
                    text = await btn.inner_text()
                    try:
                        await btn.click()
                        await page.wait_for_timeout(3000)
                        break
                    except:
                        pass
                
                await page.wait_for_timeout(3000)
                email_inputs = await page.query_selector_all('input[type="email"], input[name*="email"]')
                for inp in email_inputs:
                    try:
                        await inp.fill(temp_email)
                        print(f"Filled email: {temp_email}")
                    except:
                        pass
                
                # Look for continue/submit
                continue_btns = await page.query_selector_all('button:has-text("Continue"), button:has-text("Next"), button:has-text("Submit"), button[type="submit"]')
                for btn in continue_btns:
                    try:
                        await btn.click()
                        print("Clicked continue")
                        await page.wait_for_timeout(5000)
                        break
                    except:
                        pass
        
        # Check current state
        body_text = await page.inner_text('body')
        print(f"Current state: {body_text[:3000]}")
        
        # If wallet created, go to activations
        if "wallet" in body_text.lower() or "cube" in body_text.lower() or "activation" in body_text.lower():
            print("\n--- Going to activations ---")
            await page.goto("https://layer3.xyz/activations", wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)
            
            body_text = await page.inner_text('body')
            print(f"Activations: {body_text[:5000]}")
            
            # Look for free "Learn" quests
            learn_links = await page.query_selector_all('a:has-text("Learn"), a:has-text("Introduction"), button:has-text("Learn"), button:has-text("Introduction")')
            for link in learn_links[:10]:
                text = await link.inner_text()
                href = await link.get_attribute('href')
                print(f"Learn quest: {text.strip()} -> {href}")
                if href and ('learn' in href.lower() or 'intro' in href.lower()):
                    try:
                        await page.goto(href if href.startswith('http') else f"https://layer3.xyz{href}", wait_until="networkidle")
                        await page.wait_for_timeout(5000)
                        quest_text = await page.inner_text('body')
                        print(f"Quest page: {quest_text[:3000]}")
                        
                        # Look for "Start" or "Begin" button
                        start_btns = await page.query_selector_all('button:has-text("Start"), button:has-text("Begin"), button:has-text("Mint"), button:has-text("Complete")')
                        for sbtn in start_btns:
                            stext = await sbtn.inner_text()
                            print(f"Start button: {stext.strip()}")
                            try:
                                await sbtn.click()
                                await page.wait_for_timeout(5000)
                                print("Clicked start!")
                                result_text = await page.inner_text('body')
                                print(f"Result: {result_text[:2000]}")
                            except Exception as e:
                                print(f"Start click failed: {e}")
                        break
                    except Exception as e:
                        print(f"Quest navigation failed: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(signup_and_quest())