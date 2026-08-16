#!/usr/bin/env python3
"""Explore Microlancer.io - check React root and network."""
import asyncio
from playwright.async_api import async_playwright

async def explore_microlancer():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Capture network requests
        requests = []
        page.on("request", lambda req: requests.append(req.url))
        page.on("response", lambda resp: print(f"RESPONSE: {resp.url} - {resp.status}") if "api" in resp.url.lower() or "task" in resp.url.lower() or "job" in resp.url.lower() else None)
        
        print("🔍 Navigating to Microlancer.io...")
        await page.goto("https://microlancer.io", wait_until="networkidle", timeout=60000)
        
        # Wait longer for React to hydrate and fetch data
        await page.wait_for_timeout(15000)
        
        # Check React root
        root = await page.query_selector('#root, #app, [data-reactroot], .app, main')
        if root:
            root_text = await root.inner_text()
            print(f"=== ROOT ELEMENT TEXT (first 5000) ===")
            print(root_text[:5000])
            root_html = await root.inner_html()
            print(f"=== ROOT ELEMENT HTML (first 5000) ===")
            print(root_html[:5000])
        
        # Check body
        body_text = await page.inner_text('body')
        print(f"=== BODY TEXT (first 5000) ===")
        print(body_text[:5000] if body_text else "EMPTY")
        
        # Check all elements with text
        all_elements = await page.query_selector_all('*')
        print(f"Total DOM elements: {len(all_elements)}")
        
        # Look for text content in elements
        for el in all_elements[:200]:
            try:
                text = await el.inner_text()
                if text and len(text.strip()) > 10 and ('task' in text.lower() or 'job' in text.lower() or 'gig' in text.lower() or 'bitcoin' in text.lower() or 'lightning' in text.lower() or 'sats' in text.lower() or 'browse' in text.lower() or 'marketplace' in text.lower()):
                    tag = await el.evaluate('el => el.tagName')
                    class_name = await el.get_attribute('class')
                    print(f"  <{tag} class='{class_name}'>: {text.strip()[:200]}")
            except:
                pass
        
        # Print API requests
        print(f"\n=== API REQUESTS ===")
        for req in requests:
            if 'api' in req.lower() or 'graphql' in req.lower():
                print(f"  {req}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_microlancer())