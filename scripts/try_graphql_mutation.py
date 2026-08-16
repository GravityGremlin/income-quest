#!/usr/bin/env python3
"""
Try to set username via GraphQL API using existing cookies.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Load cookies
        with open('/home/user/income-quest/data/stacker_news_cookies_fresh.json', 'r') as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        # Try GraphQL introspection first
        introspection_query = """
        query {
            __schema {
                mutationType {
                    fields {
                        name
                        description
                    }
                }
            }
        }
        """
        
        result = await page.evaluate("""
            (async () => {
                const query = `%s`;
                const response = await fetch("https://stacker.news/api/graphql", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    credentials: "include",
                    body: JSON.stringify({ query })
                });
                return response.json();
            })()
        """ % introspection_query.replace('\n', '\\n').replace('"', '\\"'))
        
        print(f"Introspection result: {json.dumps(result, indent=2)}")
        
        # Check for profile/user mutations
        if 'data' in result and '__schema' in result['data']:
            mutations = result['data']['__schema']['mutationType']['fields']
            for field in mutations:
                name = field['name'].lower()
                if any(kw in name for kw in ['profile', 'user', 'name', 'username', 'update', 'edit']):
                    print(f"  Relevant mutation: {field['name']}: {field.get('description', '')}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())