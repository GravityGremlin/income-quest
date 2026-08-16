#!/usr/bin/env python3
"""
Test GraphQL with different cookie combinations.
"""
import json
import requests

# Load cookies
with open('/home/user/income-quest/data/stacker_news_cookies_fresh.json', 'r') as f:
    cookies_list = json.load(f)

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

query = "{ blockHeight }"

# Test 1: No cookies
print("=== No cookies ===")
r = requests.post("https://stacker.news/api/graphql", headers=headers, json={"query": query}, timeout=10)
print(f"Status: {r.status_code}, Result: {r.json()}")

# Test 2: Only aws-waf-token
print("\n=== aws-waf-token only ===")
cookies = {c['name']: c['value'] for c in cookies_list if c['name'] == 'aws-waf-token'}
r = requests.post("https://stacker.news/api/graphql", headers=headers, cookies=cookies, json={"query": query}, timeout=10)
print(f"Status: {r.status_code}, Result: {r.json()}")

# Test 3: All except aws-waf-token
print("\n=== All except aws-waf-token ===")
cookies = {c['name']: c['value'] for c in cookies_list if 'stacker.news' in c.get('domain', '') and c['name'] != 'aws-waf-token'}
r = requests.post("https://stacker.news/api/graphql", headers=headers, cookies=cookies, json={"query": query}, timeout=10)
print(f"Status: {r.status_code}, Result: {r.json()}")

# Test 4: All stacker.news cookies
print("\n=== All stacker.news cookies ===")
cookies = {c['name']: c['value'] for c in cookies_list if 'stacker.news' in c.get('domain', '')}
r = requests.post("https://stacker.news/api/graphql", headers=headers, cookies=cookies, json={"query": query}, timeout=10)
print(f"Status: {r.status_code}, Result: {r.json()}")