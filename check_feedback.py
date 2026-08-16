import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Login first to SatsBoard
        await page.goto('https://sats.throbbing.click/auth/login', wait_until='networkidle')
        await page.wait_for_timeout(2000)
        await page.fill('input[name="lightning_address"]', 'gravityquest@coinos.io')
        await page.wait_for_timeout(1000)
        await page.click('button:has-text("Continue with Lightning")')
        await page.wait_for_timeout(5000)
        
        # Check my feedback page for all feedback
        await page.goto('https://sats.throbbing.click/auth/feedback', wait_until='networkidle')
        await page.wait_for_timeout(5000)
        
        content = await page.content()
        # Find all feedback items
        feedback_sections = re.findall(r'<div class="feedback-message"[^>]*>.*?</div>\s*</div>\s*</div>', content, re.DOTALL)
        print(f'Found {len(feedback_sections)} feedback messages')
        for i, fb in enumerate(feedback_sections[:5]):
            print(f'\n--- Feedback {i+1} ---')
            # Extract text content
            text = re.sub(r'<[^>]+>', '', fb)
            text = text.replace('&', '&').replace('<', '<').replace('>', '>').replace('"', '"').replace("'", "'")
            print(text[:2000])
        
        await browser.close()

asyncio.run(main())