#!/usr/bin/env python3
"""Explore Galxe API endpoints from network analysis."""
import asyncio
import httpx
import json

async def explore_galxe_api():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Origin': 'https://app.galxe.com',
        'Referer': 'https://app.galxe.com/',
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
        # Try different GraphQL endpoints
        endpoints = [
            "https://graphql.galxe.com/graphql",
            "https://api.galxe.com/graphql",
            "https://app.galxe.com/api/graphql",
            "https://galxe.com/graphql",
            "https://api.galxe.com/v1/graphql",
        ]
        
        for endpoint in endpoints:
            print(f"\n🔍 Testing {endpoint}...")
            try:
                resp = await client.post(endpoint, json={"query": "{ __schema { queryType { name } } }"})
                print(f"Status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"Response: {resp.text[:500]}")
            except Exception as e:
                print(f"Error: {e}")
        
        # Check for REST API endpoints
        rest_endpoints = [
            "https://api.galxe.com/v1/quests",
            "https://api.galxe.com/v1/spaces",
            "https://app.galxe.com/api/quests",
            "https://galxe.com/api/quests",
        ]
        
        for endpoint in rest_endpoints:
            print(f"\n🔍 Testing REST {endpoint}...")
            try:
                resp = await client.get(endpoint)
                print(f"Status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"Response: {resp.text[:500]}")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(explore_galxe_api())