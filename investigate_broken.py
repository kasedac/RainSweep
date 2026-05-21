import asyncio
import httpx


async def check(url: str, name: str):
    print(f"=== Testing {name}: {url} ===")
    headers_browser = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Referer": "https://raindrop.io/",
    }

    clients = [
        (
            "Browser-like",
            httpx.AsyncClient(
                headers=headers_browser, follow_redirects=True, timeout=30.0
            ),
        ),
        ("Default (No UA)", httpx.AsyncClient(follow_redirects=True, timeout=30.0)),
    ]

    for label, client in clients:
        print(f"[{label}]")
        try:
            # Try HEAD
            resp = await client.head(url)
            print(f"  HEAD: {resp.status_code}")
            if resp.status_code != 200:
                # Try GET
                resp = await client.get(url)
                print(f"  GET:  {resp.status_code}")
        except Exception as e:
            print(f"  Error: {type(e).__name__}: {e}")
        finally:
            await client.aclose()
    print("\n")


async def main():
    targets = [
        ("L-Tike (Timeout)", "https://l-tike.com/concert/feature/perfume/25051500"),
        (
            "Biccamera (Timeout)",
            "https://www.biccamera.com/bc/c/entertainment/gundam/chronology.jsp",
        ),
        ("Medium (403)", "https://tumada.medium.com/age-of-deployment-acd88f07da59"),
        (
            "Backspace (Connect)",
            "https://blog.backspace.fm/%E6%95%85%E4%BA%BA%E3%82%B5%E3%82%A4%E3%83%88-%E3%81%AB%E8%BC%89%E3%81%A3%E3%81%9F%E8%A9%B1-6bdac72e175d",
        ),
    ]
    for name, url in targets:
        await check(url, name)


if __name__ == "__main__":
    asyncio.run(main())
