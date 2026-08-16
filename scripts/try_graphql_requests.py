#!/usr/bin/env python3
"""
Try GraphQL API using requests library with cookies.
"""
import json
import requests

# Load cookies
with open('/home/user/income-quest/data/stacker_news_cookies_fresh.json', 'r') as f:
    cookies_list = json.load(f)

# Convert to dict for requests
cookies = {c['name']: c['value'] for c in cookies_list if 'stacker.news' in c.get('domain', '')}
print(f"Using cookies: {list(cookies.keys())}")

# GraphQL introspection
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

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

response = requests.post(
    "https://stacker.news/api/graphql",
    headers=headers,
    cookies=cookies,
    json={"query": introspection_query}
)

print(f"Status: {response.status_code}")
result = response.json()
print(f"Result: {json.dumps(result, indent=2)}")

# Check for profile/user mutations
if 'data' in result and '__schema' in result['data']:
    mutations = result['data']['__schema']['mutationType']['fields']
    for field in mutations:
        name = field['name'].lower()
        if any(kw in name for kw in ['profile', 'user', 'name', 'username', 'update', 'edit']):
            print(f"  Relevant mutation: {field['name']}: {field.get('description', '')}")