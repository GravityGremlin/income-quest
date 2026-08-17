#!/usr/bin/env python3
"""Explore Galxe authentication and API endpoints."""
import asyncio
import httpx
from bs4 import BeautifulSoup
import json
import re

async def explore_galxe_auth():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
        # First, let's check the login page
        print("🔍 Checking login/authentication...")
        resp = await client.get("https://app.galxe.com/login")
        print(f"Login page status: {resp.status_code}")
        print(f"Final URL: {resp.url}")
        
        with open("/home/user/income-quest/galxe_login.html", "w") as f:
            f.write(resp.text)
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        body_text = soup.get_text()[:5000]
        print(f"Login page text: {body_text[:2000]}")
        
        # Look for wallet connect options
        buttons = soup.find_all('button')
        for btn in buttons:
            text = btn.get_text(strip=True)
            if text:
                print(f"Button: {text[:100]}")
        
        # Check for forms
        forms = soup.find_all('form')
        for form in forms:
            print(f"Form: action={form.get('action')}, method={form.get('method')}")
            inputs = form.find_all('input')
            for inp in inputs:
                print(f"  Input: name={inp.get('name')}, type={inp.get('type')}, placeholder={inp.get('placeholder')}")
        
        # Check for any API endpoints in script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('api' in script.string.lower() or 'graphql' in script.string.lower() or 'auth' in script.string.lower()):
                print(f"Script with API/auth: {script.string[:500]}")
        
        # Check if there's a GraphQL endpoint
        # Try common GraphQL endpoints
        print("\n🔍 Testing GraphQL endpoint...")
        graphql_resp = await client.post("https://app.galxe.com/graphql", json={"query": "{ __schema { types { name } } }"})
        print(f"GraphQL status: {graphql_resp.status_code}")
        if graphql_resp.status_code == 200:
            print(f"GraphQL response: {graphql_resp.text[:1000]}")

if __name__ == "__main__":
    asyncio.run(explore_galxe_auth())