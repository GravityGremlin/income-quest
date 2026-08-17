#!/usr/bin/env python3
"""Try Layer3 Sign up and Layer3 Wallet creation."""
import asyncio
from playwright.async_api import async_playwright

async def layer3_signup():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Go to app
        print("Going to app.layer3.xyz/discover...")
        await page.goto("https://app.layer3.xyz/discover", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Click "Sign up"
        signup_btn = await page.query_selector('button:has-text("Sign up"), a:has-text("Sign up")')
        if signup_btn:
            await signup_btn.click()
            await page.wait_for_timeout(3000)
            print("Clicked Sign up")
        
        body_text = await page.inner_text('body')
        print(f"After Sign up: {body_text[:3000]}")
        
        # Look for wallet options
        wallet_btns = await page.query_selector_all('button:has-text("Layer3 Wallet"), button:has-text("Create Wallet"), button:has-text("Continue with"), button:has-text("Email"), button:has-text("Google"), button:has-text("Twitter"), button:has-text("Discord")')
        for btn in wallet_btns:
            text = await btn.inner_text()
            print(f"Wallet/Auth option: {text.strip()}")
            try:
                await btn.click()
                await page.wait_for_timeout(3000)
                new_text = await page.inner_text('body')
                print(f"After click: {new_text[:2000]}")
            except Exception as e:
                print(f"Click failed: {e}")
        
        # Check for email input
        await page.wait_for_timeout(3000)
        body_text = await page.inner_text('body')
        print(f"Current state: {body_text[:3000]}")
        
        email_inputs = await page.query_selector_all('input[type="email"], input[name*="email"]')
        print(f"Email inputs: {len(email_inputs)}")
        
        if email_inputs:
            # Get temp email
            await page.goto("https://www.guerrillamail.com", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            email_elem = await page.query_selector('#email-widget, #inbox-id, .email-address, #email_addr, input[readonly]')
            temp_email = ""
            if email_elem:
                temp_email = await email_elem.inner_text()
                temp_email = temp_email.strip()
                if not temp_email or '@' not in temp_email:
                    temp_email = await email_elem.get_attribute('value')
            print(f"Temp email: {temp_email}")
            
            if temp_email and '@' in temp_email:
                await page.goto("https://app.layer3.xyz/discover", wait_until="networkidle")
                await page.wait_for_timeout(3000)
                
                # Re-click sign up
                signup_btn = await page.query_selector('button:has-text("Sign up"), a:has-text("Sign up")')
                if signup_btn:
                    await signup_btn.click()
                    await page.wait_for_timeout(3000)
                
                # Click Layer3 Wallet option
                wallet_btns = await page.query_selector_all('button:has-text("Layer3 Wallet"), button:has-text("Create Wallet")')
                for btn in wallet_btns:
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
                
                # Continue
                continue_btns = await page.query_selector_all('button:has-text("Continue"), button:has-text("Next"), button[type="submit"]')
                for btn in continue_btns:
                    try:
                        await btn.click()
                        print("Clicked continue")
                        await page.wait_for_timeout(5000)
                        break
                    except:
                        pass
        
        # Final check
        await page.wait_for_timeout(3000)
        body_text = await page.inner_text('body')
        print(f"Final state: {body_text[:3000]}")
        
        # If wallet created, try a Learn quest
        if 'wallet' in body_text.lower() or 'address' in body_text.lower() or 'cube' in body_text.lower():
            print("\nWallet connected! Trying Learn quest...")
            
            # Click "Learn" tab/category
            learn_tab = await page.query_selector('button:has-text("Learn"), a:has-text("Learn"), [role="tab"]:has-text("Learn")')
            if learn_tab:
                await learn_tab.click()
                await page.wait_for_timeout(3000)
                learn_text = await page.inner_text('body')
                print(f"Learn tab: {learn_text[:2000]}")
            
            # Find first Learn quest
            quest_links = await page.query_selector_all('a[href*="learn"], a[href*="intro"], a[href*="introduction"]')
            for link in quest_links[:5]:
                href = await link.get_attribute('href')
                text = await link.inner_text()
                print(f"Quest: {text.strip()} -> {href}")
                if href:
                    try:
                        full_url = href if href.startswith('http') else f"https://app.layer3.xyz{href}"
                        await page.goto(full_url, wait_until="networkidle")
                        await page.wait_for_timeout(5000)
                        quest_text = await page.inner_text('body')
                        print(f"Quest page: {quest_text[:2000]}")
                        
                        start_btns = await page.query_selector_all('button:has-text("Start"), button:has-text("Begin"), button:has-text("Mint"), button:has-text("Claim")')
                        for sbtn in start_btns:
                            stext = await sbtn.inner_text()
                            print(f"  Start: {stext.strip()}")
                            try:
                                await sbtn.click()
                                await page.wait_for_timeout(5000)
                                result = await page.inner_text('body')
                                print(f"  Result: {result[:2000]}")
                            except Exception as e:
                                print(f"  Click failed: {e}")
                        break
                    except Exception as e:
                        print(f"Quest nav failed: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(layer3_signup())