#!/usr/bin/env python3
"""
Check the actual email content from Guerrilla Mail for Stacker News.
"""
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Go to Guerrilla Mail and check the email
        page = await context.new_page()
        await page.goto("https://www.guerrillamail.com/", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # Get email address
        email_elem = await page.query_selector('#email-widget, input[name="email"]')
        email = await email_elem.get_attribute('value') if email_elem else None
        print(f"Email: {email}")
        
        # Wait for email
        await page.wait_for_timeout(10000)
        
        # Click on the email to view it
        email_rows = await page.query_selector_all('tr[onclick*="open"], tr.email-row, .email-item, tbody tr')
        print(f"Email rows: {len(email_rows)}")
        
        for row in email_rows[:5]:
            text = await row.text_content()
            if 'stacker' in text.lower() or 'magic' in text.lower() or 'code' in text.lower():
                print(f"Found Stacker email: {text[:200]}")
                # Click to open
                await row.click()
                await page.wait_for_timeout(3000)
                break
        
        # Get full page content
        content = await page.content()
        with open('/home/user/income-quest/data/guerrilla_full.html', 'w') as f:
            f.write(content)
        
        # Extract email body
        import re
        # Look for magic code or link
        text = await page.text_content('body')
        print("\n=== GUERRILLA MAIL PAGE TEXT ===")
        print(text[:5000])
        
        # Search for stacker content
        stacker_matches = re.findall(r'[Ss]tacker[^<>{}]{0,200}', text)
        for m in stacker_matches[:10]:
            print(f"Stacker match: {m}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())