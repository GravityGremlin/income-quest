#!/usr/bin/env python3
"""
Monitor GraphQL requests during magic code submission.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        graphql_requests = []
        graphql_responses = []
        
        context.on("request", lambda req: graphql_requests.append((req.url, req.post_data)) if 'graphql' in req.url else None)
        context.on("response", lambda resp: graphql_responses.append((resp.status, resp.url, resp)) if 'graphql' in resp.url else None)
        
        page = await context.new_page()
        await page.goto("https://stacker.news/email", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        # Enable inputs
        await page.evaluate('''
            document.querySelectorAll('input[name="token"]').forEach(el => {
                el.disabled = false;
                el.readOnly = false;
            });
        ''')
        
        # Fill with dummy code
        await page.evaluate('''
            const inputs = document.querySelectorAll('input[name="token"]');
            const code = "123456";
            inputs.forEach((el, i) => { el.value = code[i]; });
        ''')
        
        # Submit
        await page.evaluate('''
            const form = document.querySelector('form');
            if (form) {
                form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
            }
        ''')
        
        await page.wait_for_timeout(5000)
        
        # Print GraphQL requests
        print("=== GRAPHQL REQUESTS ===")
        for url, data in graphql_requests:
            print(f"  {url}")
            if data:
                print(f"    {data[:500]}")
        
        print("\n=== GRAPHQL RESPONSES ===")
        for status, url, resp in graphql_responses:
            print(f"  {status} {url}")
            # Try to get response body
            try:
                body = await resp.json()
                print(f"    {json.dumps(body)[:500]}")
            except:
                try:
                    text = await resp.text()
                    print(f"    {text[:500]}")
                except:
                    pass
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())