import httpx
import asyncio
from typing import Tuple


class LinkChecker:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    async def is_broken(self, url: str) -> Tuple[bool, str]:
        headers = {
            "User-Agent": self.USER_AGENT,
            "Referer": "https://raindrop.io/",
        }
        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            max_attempts = 5
            base_delay = 5
            last_reason = "Unknown"

            for attempt in range(max_attempts):
                try:
                    # Try HEAD first
                    response = await client.head(url, follow_redirects=True)

                    if response.status_code == 429:
                        delay = base_delay * (2**attempt)
                        print(
                            f"\n[429] Rate limited for {url}. Retrying in {delay}s... (Attempt {attempt + 1}/{max_attempts})"
                        )
                        await asyncio.sleep(delay)
                        last_reason = "429 Too Many Requests"
                        continue

                    # If HEAD fails or returns non-200, try GET before deciding it's broken
                    if response.status_code != 200:
                        response = await client.get(url, follow_redirects=True)

                        if response.status_code == 429:
                            delay = base_delay * (2**attempt)
                            print(
                                f"\n[429] Rate limited for {url}. Retrying in {delay}s... (Attempt {attempt + 1}/{max_attempts})"
                            )
                            await asyncio.sleep(delay)
                            last_reason = "429 Too Many Requests"
                            continue

                    if response.status_code == 200:
                        return False, "OK"

                    last_reason = f"Status {response.status_code}"

                except asyncio.TimeoutError:
                    last_reason = "Timeout"
                except httpx.HTTPError as e:
                    last_reason = f"HTTP Error: {type(e).__name__}"

                if attempt < max_attempts - 1:
                    await asyncio.sleep(base_delay)

            return True, last_reason
