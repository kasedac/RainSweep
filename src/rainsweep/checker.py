import httpx
import asyncio
from typing import Tuple
from enum import Enum


class LinkStatus(Enum):
    ALIVE = "alive"
    BROKEN = "broken"
    WARNING = "warning"


class LinkChecker:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    async def check_link(
        self, url: str, preferred_ua: str = None
    ) -> Tuple[LinkStatus, str, str | None]:
        browser_headers = {
            "User-Agent": self.USER_AGENT,
            "Referer": "https://raindrop.io/",
        }
        default_headers = {
            "Referer": "https://raindrop.io/",
        }

        max_attempts = 3
        base_delay = 5
        last_reason = "Unknown"
        verify_ssl = True
        attempt = 0

        # Set initial UA
        if preferred_ua == "default":
            current_headers = default_headers
            current_ua_type = "default"
        else:
            current_headers = browser_headers
            current_ua_type = "browser"

        while attempt < max_attempts:
            try:
                async with httpx.AsyncClient(timeout=30.0, verify=verify_ssl) as client:
                    # Try HEAD first
                    try:
                        response = await client.head(
                            url, headers=current_headers, follow_redirects=True
                        )
                    except (asyncio.TimeoutError, httpx.TimeoutException):
                        # If HEAD timeouts, try GET immediately (this is usually fine)
                        response = await client.get(
                            url, headers=current_headers, follow_redirects=True
                        )

                    # 429 logic: If we hit 429, we MUST wait before any retry.
                    if response.status_code == 429:
                        delay = base_delay * (2**attempt)
                        print(
                            f"\n[429] Rate limited for {url}. Waiting {delay}s before retry..."
                        )
                        await asyncio.sleep(delay)

                        # After wait, if we were using browser UA, try switching to default
                        if current_ua_type == "browser":
                            print(f"Switching to default UA for {url} after 429.")
                            current_headers = default_headers
                            current_ua_type = "default"
                        
                        last_reason = "429 Too Many Requests"
                        attempt += 1
                        continue

                    # 403 logic: Potential block, switch UA and retry with delay
                    if response.status_code == 403 and current_ua_type == "browser":
                        print(
                            f"\n[403] Potential block for {url} with browser UA. Waiting {base_delay}s and switching to default UA..."
                        )
                        await asyncio.sleep(base_delay)
                        current_headers = default_headers
                        current_ua_type = "default"
                        attempt += 1
                        continue

                    # If HEAD fails or returns non-200, try GET before deciding it's broken
                    if response.status_code != 200:
                        response = await client.get(
                            url, headers=current_headers, follow_redirects=True
                        )

                        if response.status_code == 429:
                            delay = base_delay * (2**attempt)
                            print(
                                f"\n[429] Rate limited for {url} (GET). Waiting {delay}s before retry..."
                            )
                            await asyncio.sleep(delay)
                            if current_ua_type == "browser":
                                current_headers = default_headers
                                current_ua_type = "default"
                            last_reason = "429 Too Many Requests"
                            attempt += 1
                            continue

                    if 200 <= response.status_code < 300:
                        return LinkStatus.ALIVE, "OK", current_ua_type

                    if response.status_code in (404, 410):
                        return LinkStatus.BROKEN, f"Status {response.status_code}", None

                    last_reason = f"Status {response.status_code}"

            except httpx.ConnectError as e:
                if verify_ssl:
                    print(f"\n[SSL Error] {url}: {e}. Retrying without verification...")
                    verify_ssl = False
                    # Retry immediately without verification, don't increment attempt
                    continue
                last_reason = f"SSL Error: {type(e).__name__}"
            except (asyncio.TimeoutError, httpx.TimeoutException):
                last_reason = "Timeout"
            except httpx.HTTPError as e:
                last_reason = f"HTTP Error: {type(e).__name__}"

            attempt += 1
            if attempt < max_attempts:
                await asyncio.sleep(base_delay)

        return LinkStatus.WARNING, last_reason, None
