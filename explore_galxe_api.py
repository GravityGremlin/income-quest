#!/usr/bin/env python3
"""Explore Galxe GraphQL API endpoints."""
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
        # Try GraphQL endpoint
        print("🔍 Testing GraphQL endpoint...")
        
        # Introspection query
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType { name }
                mutationType { name }
                types {
                    name
                    kind
                    description
                    fields(includeDeprecated: true) {
                        name
                        description
                        type { name kind ofType { name kind } }
                    }
                }
            }
        }
        """
        
        resp = await client.post("https://app.galxe.com/graphql", json={"query": introspection_query})
        print(f"GraphQL introspection status: {resp.status_code}")
        if resp.status_code == 200:
            with open("/home/user/income-quest/galxe_graphql_schema.json", "w") as f:
                json.dump(resp.json(), f, indent=2)
            print("Schema saved to galxe_graphql_schema.json")
            # Print query type fields
            data = resp.json()
            if 'data' in data and '__schema' in data['data']:
                query_type = data['data']['__schema']['queryType']
                if query_type:
                    print(f"Query type: {query_type['name']}")
                    for t in data['data']['__schema']['types']:
                        if t['name'] == query_type['name'] and t['fields']:
                            print(f"Available queries ({len(t['fields'])}):")
                            for field in t['fields'][:30]:
                                print(f"  {field['name']}: {field.get('description', '')[:100]}")
        
        # Try to get user quests / daily quests
        print("\n🔍 Trying to get quest data...")
        quest_query = """
        query GetQuests {
            quests {
                id
                name
                description
                status
                reward
                tasks {
                    id
                    name
                    description
                    type
                    status
                    reward
                }
            }
        }
        """
        
        resp = await client.post("https://app.galxe.com/graphql", json={"query": quest_query})
        print(f"Quest query status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Response: {resp.text[:2000]}")
        
        # Try spaces query
        spaces_query = """
        query GetSpaces {
            spaces {
                id
                name
                description
                quests {
                    id
                    name
                    status
                    reward
                }
            }
        }
        """
        
        resp = await client.post("https://app.galxe.com/graphql", json={"query": spaces_query})
        print(f"Spaces query status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Response: {resp.text[:2000]}")

if __name__ == "__main__":
    asyncio.run(explore_galxe_api())