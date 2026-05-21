import httpx
import asyncio


class LinkChecker:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    async def is_broken(self, url: str) -> bool:
        headers = {"User-Agent": self.USER_AGENT}
        async with httpx.AsyncClient(headers=headers) as client:
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Try HEAD first
                    response = await client.head(url, follow_redirects=True)

                    # If HEAD fails or returns non-200, try GET before deciding it's broken
                    if response.status_code != 200:
                        response = await client.get(url, follow_redirects=True)

                    if response.status_code == 200:
                        return False

                    # Handle 429 Too Many Requests
                    if response.status_code == 429:
                        if attempt < max_attempts - 1:
                            await asyncio.sleep(10)
                            continue
                except httpx.HTTPError:
                    pass

                if attempt < max_attempts - 1:
                    await asyncio.sleep(5)

            return True
