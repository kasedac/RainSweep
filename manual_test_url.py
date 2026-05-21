import asyncio
import httpx


async def test_url(url: str):
    print(f"Testing URL: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(
        headers=headers, follow_redirects=True, timeout=10.0
    ) as client:
        try:
            print("--- HEAD request ---")
            resp_head = await client.head(url)
            print(f"Status: {resp_head.status_code}")
            print(f"Headers: {dict(resp_head.headers)}")

            print("--- GET request ---")
            resp_get = await client.get(url)
            print(f"Status: {resp_get.status_code}")

        except Exception as e:
            print(f"Exception: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_url("https://camel.hatenablog.jp/entry/instrumental-music"))
