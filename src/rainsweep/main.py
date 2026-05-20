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
    parser.add_argument(
        "--export",
        type=str,
        metavar="FILE",
        help="Export broken link IDs and URLs to a file",
    )
    parser.add_argument(
        "--import",
        dest="import_file",
        type=str,
        metavar="FILE",
        help="Import broken link IDs from a file and move them to trash (skips checking)",
    )
    return parser.parse_args()


async def amain():
    load_dotenv()
    args = parse_args()

    try:
        client = RaindropClient(token=args.token)
        checker = LinkChecker()
        cleaner = Cleaner(
            client, checker, dry_run=args.dry_run, export_file=args.export
        )

        if args.import_file:
            await cleaner.run_import(args.import_file)
        else:
            await cleaner.run()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    asyncio.run(amain())


if __name__ == "__main__":
    main()
