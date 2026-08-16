#!/usr/bin/env python3
"""
Try setName mutation correctly.
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

# Try setName mutation - returns String
username = "agent_gravity123"
mutation = f"""
mutation {{
    setName(name: "{username}")
}}
"""

response = requests.post(
    "https://stacker.news/api/graphql",
    headers=headers,
    cookies=cookies,
    json={"query": mutation}
)

print(f"Status: {response.status_code}")
result = response.json()
print(f"Result: {json.dumps(result, indent=2)}")

# Check current user
query = """
query {
    me {
        id
        name
        optional {
            stacked
        }
    }
}
"""

response2 = requests.post(
    "https://stacker.news/api/graphql",
    headers=headers,
    cookies=cookies,
    json={"query": query}
)

print(f"\nMe query status: {response2.status_code}")
print(f"Me query result: {json.dumps(response2.json(), indent=2)}")