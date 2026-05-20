import asyncio
from .client import RaindropClient
from .checker import LinkChecker


class Cleaner:
    """Orchestrates fetching, checking, and moving bookmarks."""

    def __init__(
        self, client: RaindropClient, checker: LinkChecker, dry_run: bool = False
    ):
        self.client = client
        self.checker = checker
        self.dry_run = dry_run
        self.results = {"total": 0, "broken": 0, "moved": 0}

    async def run(self):
        """Run the cleaning process."""
        print("Fetching bookmarks...")
        bookmarks = self.client.get_all_bookmarks()
        total_bookmarks = len(bookmarks)
        self.results["total"] = total_bookmarks
        print(f"Found {total_bookmarks} bookmarks.")

        broken_ids = []
        for i, bookmark in enumerate(bookmarks, 1):
            url = bookmark.link
            print(f"Checking {i}/{total_bookmarks}: {url}...", end="\r")

            is_broken = await self.checker.is_broken(url)
            if is_broken:
                self.results["broken"] += 1
                if self.dry_run:
                    print(f"\n[Dry-run] Broken: {url} (would be moved to trash)")
                else:
                    print(f"\nBroken bookmark found: {url}")
                    broken_ids.append(bookmark._id)

            # Rate limit mitigation: sleep between checks
            if i < total_bookmarks:
                await asyncio.sleep(0.5)

        if not self.dry_run and broken_ids:
            print(f"\nMoving {len(broken_ids)} broken bookmarks to trash...")
            self.client.move_to_trash_batch(broken_ids)
            self.results["moved"] = len(broken_ids)

        print("\n\nCleaning complete.")
        print(f"Total checked: {self.results['total']}")
        print(f"Total broken:  {self.results['broken']}")
        if self.dry_run:
            print(f"Total would be moved: {self.results['broken']}")
        else:
            print(f"Total moved:  {self.results['moved']}")

    def get_summary(self):
        return self.results
