#!/usr/bin/env python3
"""
Check SatsBoard for new agent-accessible tasks.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        page = await context.new_page()
        await page.goto("https://satsboard.com/", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        content = await page.content()
        with open('/home/user/income-quest/data/satsboard.html', 'w') as f:
            f.write(content)
        
        # Extract text
        text = await page.text_content('body')
        print("=== SATSBOARD PAGE TEXT (first 5000) ===")
        print(text[:5000])
        
        # Look for task listings
        import re
        # Look for sats amounts
        sats_matches = re.findall(r'(\d+,?\d*)\s*sats?', text, re.IGNORECASE)
        if sats_matches:
            print(f"\nSats amounts found: {sats_matches[:20]}")
        
        # Look for task titles/descriptions
        lines = text.split('\n')
        task_lines = [l for l in lines if any(kw in l.lower() for kw in ['task', 'bounty', 'reward', 'hiring', 'looking for', 'need', 'wanted'])]
        print(f"\nPotential task lines ({len(task_lines)}):")
        for l in task_lines[:20]:
            print(f"  {l.strip()[:200]}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())