import asyncio
import random
from .client import RaindropClient
from .checker import LinkChecker, LinkStatus


class Cleaner:
    """Orchestrates fetching, checking, and moving bookmarks."""

    def __init__(
        self,
        client: RaindropClient,
        checker: LinkChecker,
        dry_run: bool = False,
        export_file: str = None,
    ):
        self.client = client
        self.checker = checker
        self.dry_run = dry_run
        self.export_file = export_file
        self.results = {"total": 0, "broken": 0, "warning": 0, "moved": 0}

    async def run(self):
        """Run the cleaning process."""
        print("Fetching bookmarks...")
        bookmarks = self.client.get_all_bookmarks()
        total_bookmarks = len(bookmarks)
        self.results["total"] = total_bookmarks
        print(f"Found {total_bookmarks} bookmarks.")

        to_export = []
        broken_ids = []
        for i, bookmark in enumerate(bookmarks, 1):
            url = bookmark.link
            print(f"Checking {i}/{total_bookmarks}: {url}...", end="\r")

            status, reason = await self.checker.check_link(url)
            if status == LinkStatus.BROKEN:
                self.results["broken"] += 1
                broken_ids.append(bookmark.id)
                to_export.append((bookmark.id, url))
                if self.dry_run:
                    print(
                        f"\n[Dry-run] Broken: {url} ({reason}) (would be moved to trash)"
                    )
                else:
                    print(f"\nBroken bookmark found: {url} ({reason})")
            elif status == LinkStatus.WARNING:
                self.results["warning"] += 1
                # Add [WARNING] prefix for export
                to_export.append((bookmark.id, f"[WARNING] {url}"))
                print(f"\n[Warning] Suspicious link: {url} ({reason})")

            # Rate limit mitigation: sleep between checks
            if i < total_bookmarks:
                await asyncio.sleep(0.5 + random.uniform(0, 1.0))

        if self.export_file:
            print(f"\nExporting {len(to_export)} items to {self.export_file}...")
            with open(self.export_file, "w") as f:
                for b_id, b_url in to_export:
                    f.write(f"{b_id}\t{b_url}\n")

        if not self.dry_run and broken_ids:
            print(f"\nMoving {len(broken_ids)} broken bookmarks to trash...")
            self.client.move_to_trash_batch(broken_ids)
            self.results["moved"] = len(broken_ids)

        print("\n\nCleaning complete.")
        print(f"Total checked:  {self.results['total']}")
        print(f"Total broken:   {self.results['broken']}")
        print(f"Total warnings: {self.results['warning']}")
        if self.dry_run:
            print(f"Total would be moved: {self.results['broken']}")
        else:
            print(f"Total moved:    {self.results['moved']}")

    async def run_import(self, import_file: str):
        """Import broken link IDs from a file and move them to trash."""
        print(f"Importing IDs from {import_file}...")
        ids = []
        try:
            with open(import_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or "[WARNING]" in line:
                        if "[WARNING]" in line:
                            print(f"Skipping warning item: {line}")
                        continue
                    # Format is "ID\tURL" or just "ID"
                    parts = line.split("\t")
                    try:
                        ids.append(int(parts[0]))
                    except ValueError:
                        print(f"Skipping invalid line: {line}")
        except FileNotFoundError:
            print(f"Error: File {import_file} not found.")
            return

        if not ids:
            print("No IDs found to move.")
            return

        self.results["total"] = 0  # We didn't check any
        self.results["broken"] = len(ids)

        if self.dry_run:
            print(f"[Dry-run] Would move {len(ids)} bookmarks to trash.")
            self.results["moved"] = 0
        else:
            print(f"Moving {len(ids)} bookmarks to trash...")
            self.client.move_to_trash_batch(ids)
            self.results["moved"] = len(ids)

        print("\nImport and cleaning complete.")
        print(f"Total moved: {self.results['moved']}")

    def get_summary(self):
        return self.results
