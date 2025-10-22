#!/usr/bin/env python3
"""
Check available endpoints
"""

import asyncio
import aiohttp
import json

async def check_endpoints():
    """Check what endpoints are available"""
    endpoints_to_check = [
        "/",
        "/health",
        "/docs",
        "/api/v1/auth/register",
        "/api/v1/users/me",
        "/api/v1/projects",
        "/api/v1/logs",
        "/api/v1/analytics",
        "/api/v1/chat",
        "/api/v1/llm",
        "/api/v1/rag",
        "/api/v1/live-logs",
        "/api/v1/settings",
        "/security/status",
        "/database/health"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_check:
            try:
                async with session.get(f"http://localhost:8000{endpoint}") as response:
                    print(f"{endpoint}: {response.status}")
                    if response.status == 200:
                        try:
                            data = await response.json()
                            print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
                        except:
                            print(f"  Response: HTML/Text content")
                    elif response.status == 404:
                        print(f"  Not Found")
                    elif response.status == 405:
                        print(f"  Method Not Allowed")
                    else:
                        print(f"  Error: {response.status}")
            except Exception as e:
                print(f"{endpoint}: ERROR - {e}")
            print()

if __name__ == "__main__":
    asyncio.run(check_endpoints())
