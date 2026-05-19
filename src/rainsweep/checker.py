import httpx
import asyncio

class LinkChecker:
    async def is_broken(self, url: str) -> bool:
        async with httpx.AsyncClient() as client:
            for attempt in range(2):
                try:
                    # Try HEAD first
                    response = await client.head(url, follow_redirects=True)
                    
                    # If HEAD fails or returns non-200, try GET before deciding it's broken
                    if response.status_code != 200:
                        response = await client.get(url, follow_redirects=True)
                    
                    if response.status_code == 200:
                        return False
                except httpx.HTTPError:
                    pass
                
                if attempt == 0:
                    await asyncio.sleep(5)
            
            return True
