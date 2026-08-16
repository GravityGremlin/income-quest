#!/usr/bin/env python3
"""
Test GraphQL with simple query first.
"""
import json
import requests

# Load cookies
with open('/home/user/income-quest/data/stacker_news_cookies_fresh.json', 'r') as f:
    cookies_list = json.load(f)

cookies = {c['name']: c['value'] for c in cookies_list if 'stacker.news' in c.get('domain', '')}
print(f"Using cookies: {list(cookies.keys())}")

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Simple query
query = """
query {
    blockHeight
    price
}
"""

response = requests.post(
    "https://stacker.news/api/graphql",
    headers=headers,
    cookies=cookies,
    json={"query": query},
    timeout=10
)

print(f"Status: {response.status_code}")
print(f"Result: {json.dumps(response.json(), indent=2)}")