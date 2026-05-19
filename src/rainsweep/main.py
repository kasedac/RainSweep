import argparse
import asyncio
import sys
from dotenv import load_dotenv
from .client import RaindropClient
from .checker import LinkChecker
from .cleaner import Cleaner


def parse_args():
    parser = argparse.ArgumentParser(
        description="RainSweep: Clean broken bookmarks from Raindrop.io"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without moving bookmarks to trash (only logging)",
    )
    parser.add_argument(
        "--token",
        type=str,
        help="Raindrop.io API token (overrides RAINDROP_TOKEN environment variable)",
    )
    return parser.parse_args()


async def amain():
    load_dotenv()
    args = parse_args()

    try:
        client = RaindropClient(token=args.token)
        checker = LinkChecker()
        cleaner = Cleaner(client, checker, dry_run=args.dry_run)

        await cleaner.run()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    asyncio.run(amain())


if __name__ == "__main__":
    main()
