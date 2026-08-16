#!/usr/bin/env python3
"""
Submit magic code to NextAuth callback endpoint.
"""
import json
import requests

# Load cookies
with open('/home/user/income-quest/data/stacker_news_cookies_fresh.json', 'r') as f:
    cookies_list = json.load(f)

cookies = {c['name']: c['value'] for c in cookies_list if 'stacker.news' in c.get('domain', '')}

# Get CSRF token
csrf_cookie = cookies.get('__Host-next-auth.csrf-token', '')
# The cookie value is URL-encoded, need to decode
import urllib.parse
csrf_token = urllib.parse.unquote(csrf_cookie).split('|')[0] if '|' in urllib.parse.unquote(csrf_cookie) else urllib.parse.unquote(csrf_cookie)
print(f"CSRF token: {csrf_token[:30]}...")

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
}

# Magic code from earlier
magic_code = "949494"

# Try callback endpoint
data = {
    "token": magic_code,
    "csrfToken": csrf_token,
    "callbackUrl": "https://stacker.news/",
    "json": "true"
}

r = requests.post(
    "https://stacker.news/api/auth/callback/email",
    headers=headers,
    cookies=cookies,
    data=data,
    timeout=15,
    allow_redirects=False
)

print(f"Status: {r.status_code}")
print(f"Headers: {dict(r.headers)}")
print(f"Cookies set: {r.cookies}")
print(f"Body: {r.text[:500]}")

# Check if session cookie was set
for cookie in r.cookies:
    print(f"  New cookie: {cookie.name} = {cookie.value[:50]}...")