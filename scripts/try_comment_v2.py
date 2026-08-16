#!/usr/bin/env python3
"""
Find and navigate to a post on Stacker News, try to comment.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Load cookies
        with open('/home/user/income-quest/data/stacker_news_cookies.json', 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        # Go to home page
        await page.goto("https://stacker.news/", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # Find all links to items/posts
        links = await page.query_selector_all('a[href^="/items/"]')
        print(f"Found {len(links)} item links")
        
        item_urls = []
        for link in links[:10]:
            href = await link.get_attribute('href')
            text = await link.text_content()
            if href and href not in item_urls:
                item_urls.append(href)
                print(f"  {href}: {text[:100] if text else 'no text'}")
        
        if item_urls:
            # Navigate to first item
            item_url = f"https://stacker.news{item_urls[0]}"
            print(f"\nNavigating to: {item_url}")
            
            item_page = await context.new_page()
            await item_page.goto(item_url, wait_until="networkidle")
            await item_page.wait_for_timeout(3000)
            
            content = await item_page.content()
            with open('/home/user/income-quest/data/stacker_item.html', 'w') as f:
                f.write(content)
            
            # Check for comment form
            textareas = await item_page.query_selector_all('textarea')
            print(f"\nTextareas found: {len(textareas)}")
            for ta in textareas:
                attrs = await ta.evaluate('el => ({name: el.name, placeholder: el.placeholder, id: el.id, class: el.className})')
                print(f"  {attrs}")
            
            # Look for comment/reply buttons
            buttons = await item_page.query_selector_all('button')
            print(f"\nButtons found: {len(buttons)}")
            for btn in buttons:
                text = await btn.text_content()
                cls = await btn.get_attribute('class')
                if any(kw in (text or '').lower() for kw in ['comment', 'reply', 'post', 'send', 'submit']):
                    print(f"  text='{text}', class='{cls}'")
            
            # Try to comment if textarea found
            comment_ta = await item_page.query_selector('textarea[name="comment"], textarea[placeholder*="comment" i], textarea[placeholder*="reply" i]')
            if comment_ta:
                print("\n--- Attempting to comment ---")
                await comment_ta.fill("Great insights! Thanks for sharing. ⚡")
                
                # Find submit button near the textarea
                submit_btn = await item_page.query_selector('button[type="submit"]')
                if submit_btn:
                    await submit_btn.click()
                    await item_page.wait_for_timeout(3000)
                    print("Comment submitted!")
                    
                    # Check result
                    result = await item_page.content()
                    if "Great insights" in result:
                        print("Comment appears on page!")
                    else:
                        print("Comment submitted but not visible yet (may need approval)")
            else:
                print("\nNo comment form found - may need full login/username")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())