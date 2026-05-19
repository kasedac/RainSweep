import asyncio
from typing import List, Optional
from .client import RaindropClient
from .checker import LinkChecker

class Cleaner:
    """Orchestrates fetching, checking, and moving bookmarks."""

    def __init__(self, client: RaindropClient, checker: LinkChecker, dry_run: bool = False):
        self.client = client
        self.checker = checker
        self.dry_run = dry_run
        self.results = {
            "total": 0,
            "broken": 0,
            "moved": 0
        }

    async def run(self):
        """Run the cleaning process."""
        print("Fetching bookmarks...")
        bookmarks = self.client.get_all_bookmarks()
        total_bookmarks = len(bookmarks)
        self.results["total"] = total_bookmarks
        print(f"Found {total_bookmarks} bookmarks.")

        for i, bookmark in enumerate(bookmarks, 1):
            url = bookmark.link
            print(f"Checking {i}/{total_bookmarks}: {url}...", end="\r")
            
            is_broken = await self.checker.is_broken(url)
            if is_broken:
                self.results["broken"] += 1
                if self.dry_run:
                    print(f"\n[Dry-run] Broken: {url} (would be moved to trash)")
                else:
                    print(f"\nMoving broken bookmark to trash: {url}")
                    self.client.move_to_trash(bookmark._id)
                    self.results["moved"] += 1
        
        print(f"\n\nCleaning complete.")
        print(f"Total checked: {self.results['total']}")
        print(f"Total broken:  {self.results['broken']}")
        if self.dry_run:
            print(f"Total would be moved: {self.results['broken']}")
        else:
            print(f"Total moved:  {self.results['moved']}")

    def get_summary(self):
        return self.results
