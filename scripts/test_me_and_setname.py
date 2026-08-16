#!/usr/bin/env python3
"""
Test me query and setName mutation with cookies.
"""
import json
import requests

# Load cookies
with open('/home/user/income-quest/data/stacker_news_cookies_fresh.json', 'r') as f:
    cookies_list = json.load(f)

cookies = {c['name']: c['value'] for c in cookies_list if 'stacker.news' in c.get('domain', '')}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Test me query
print("=== me query ===")
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
r = requests.post("https://stacker.news/api/graphql", headers=headers, cookies=cookies, json={"query": query}, timeout=15)
print(f"Status: {r.status_code}")
print(f"Result: {json.dumps(r.json(), indent=2)}")

# Test setName mutation
print("\n=== setName mutation ===")
mutation = """
mutation {
    setName(name: "agent_test123")
}
"""
r = requests.post("https://stacker.news/api/graphql", headers=headers, cookies=cookies, json={"query": mutation}, timeout=15)
print(f"Status: {r.status_code}")
print(f"Result: {json.dumps(r.json(), indent=2)}")