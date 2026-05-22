import asyncio
import httpx

async def check(url: str, label: str):
    print(f"--- Testing {label}: {url} ---")
    
    browser_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://raindrop.io/"
    }
    
    default_headers = {
        "Referer": "https://raindrop.io/"
    }

    async def run_test(headers, client_label):
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=10.0) as client:
            try:
                # First HEAD
                resp = await client.head(url)
                print(f"  [{client_label}] HEAD: {resp.status_code}")
                
                # If not 200, try GET
                if resp.status_code != 200:
                    resp = await client.get(url)
                    print(f"  [{client_label}] GET:  {resp.status_code}")
                return resp.status_code
            except Exception as e:
                print(f"  [{client_label}] Error: {type(e).__name__}")
                return None

    # Current logic starts with Browser UA
    print("Attempt 1: Browser UA")
    status = await run_test(browser_headers, "Browser UA")
    
    if status in (403, 429):
        print("Attempt 2: Immediate fallback to Default UA")
        await run_test(default_headers, "Default UA")

async def main():
    urls = [
        "https://takuya-1st.hatenablog.jp/entry/2017/11/20/171133",
        "https://takoratta.hatenablog.com/entry/2026/04/28/173315"
    ]
    for i, url in enumerate(urls):
        await check(url, f"Hatena {i+1}")
        await asyncio.sleep(1) # Small delay to simulate loop

if __name__ == "__main__":
    asyncio.run(main())
