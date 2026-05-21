import asyncio
import httpx


async def check(
    url: str,
    name: str,
    verify_ssl: bool = True,
    use_http2: bool = False,
    referer: str = None,
):
    print(
        f"=== Testing {name}: {url} (SSL={verify_ssl}, HTTP2={use_http2}, Ref={referer}) ==="
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    }
    if referer:
        headers["Referer"] = referer

    async with httpx.AsyncClient(
        headers=headers,
        follow_redirects=True,
        timeout=10.0,
        verify=verify_ssl,
        http2=use_http2,
    ) as client:
        try:
            resp = await client.get(url)
            print(f"  GET: {resp.status_code}")
        except Exception as e:
            print(f"  Error: {type(e).__name__}: {e}")
    print("\n")


async def main():
    # Test Backspace with SSL verify=False
    await check(
        "https://blog.backspace.fm/%E6%95%85%E4%BA%BA%E3%82%B5%E3%82%A4%E3%83%88-%E3%81%AB%E8%BC%89%E3%81%A3%E3%81%9F%E8%A9%B1-6bdac72e175d",
        "Backspace (No SSL)",
        verify_ssl=False,
    )

    # Test Medium with different Referer
    await check(
        "https://tumada.medium.com/age-of-deployment-acd88f07da59",
        "Medium (Ref=Google)",
        referer="https://www.google.com/",
    )
    await check(
        "https://tumada.medium.com/age-of-deployment-acd88f07da59", "Medium (No Ref)"
    )

    # Test L-Tike and Biccamera with HTTP/2
    await check(
        "https://l-tike.com/concert/feature/perfume/25051500",
        "L-Tike (HTTP2)",
        use_http2=True,
    )
    await check(
        "https://www.biccamera.com/bc/c/entertainment/gundam/chronology.jsp",
        "Biccamera (HTTP2)",
        use_http2=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
