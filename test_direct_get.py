import asyncio
import httpx


async def check(url: str):
    print(f"Testing {url} with direct GET and 60s timeout...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    async with httpx.AsyncClient(
        headers=headers, follow_redirects=True, timeout=60.0
    ) as client:
        try:
            resp = await client.get(url)
            print(f"  Result: {resp.status_code}")
        except Exception as e:
            print(f"  Error: {type(e).__name__}: {e}")


async def main():
    await check("https://l-tike.com/concert/feature/perfume/25051500")
    await check("https://www.biccamera.com/bc/c/entertainment/gundam/chronology.jsp")
    await check("https://tumada.medium.com/age-of-deployment-acd88f07da59")


if __name__ == "__main__":
    asyncio.run(main())
