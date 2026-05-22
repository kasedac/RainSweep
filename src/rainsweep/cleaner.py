import asyncio
import random
import time
from urllib.parse import urlparse
from typing import Dict
from .client import RaindropClient
from .checker import LinkChecker, LinkStatus
from .history import HistoryManager


class Cleaner:
    """Orchestrates fetching, checking, and moving bookmarks."""

    def __init__(
        self,
        client: RaindropClient,
        checker: LinkChecker,
        dry_run: bool = False,
        export_file: str = None,
        history_manager: HistoryManager = None,
    ):
        self.client = client
        self.checker = checker
        self.dry_run = dry_run
        self.export_file = export_file
        self.history_manager = history_manager or HistoryManager()
        self.results = {"total": 0, "broken": 0, "warning": 0, "moved": 0}
        self.domain_locks: Dict[str, asyncio.Lock] = {}
        self.global_backoff_until: float = 0

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL for per-domain rate limiting."""
        parsed = urlparse(url)
        return parsed.netloc

    async def _process_bookmark(self, bookmark, index: int, total: int) -> Tuple[Optional[int], Optional[str]]:
        """Process a single bookmark: check link, update history, and return info if broken/warning."""
        url = bookmark.link
        domain = self._get_domain(url)

        # Global backoff check
        while time.time() < self.global_backoff_until:
            wait_time = self.global_backoff_until - time.time()
            print(f"\n[Global Backoff] Waiting {wait_time:.1f}s before next request...")
            await asyncio.sleep(wait_time)

        # Per-domain lock
        if domain not in self.domain_locks:
            self.domain_locks[domain] = asyncio.Lock()

        async with self.domain_locks[domain]:
            print(f"Checking {index}/{total}: {url}...", end="\r")

            preferred_ua = self.history_manager.get_preferred_ua(url)
            
            def set_global_backoff(duration: float):
                self.global_backoff_until = time.time() + duration

            status, reason, worked_ua = await self.checker.check_link(
                url, preferred_ua=preferred_ua, on_429=set_global_backoff
            )

            if status == LinkStatus.ALIVE:
                if worked_ua:
                    self.history_manager.update_domain_rule(url, worked_ua)
                return None, None
            elif status == LinkStatus.BROKEN:
                self.results["broken"] += 1
                if self.dry_run:
                    print(f"\n[Dry-run] Broken: {url} ({reason}) (would be moved to trash)")
                else:
                    print(f"\nBroken bookmark found: {url} ({reason})")
                return bookmark.id, url
            elif status == LinkStatus.WARNING:
                self.results["warning"] += 1
                print(f"\n[Warning] Suspicious link: {url} ({reason})")
                return bookmark.id, f"[WARNING] {url}"
        
        return None, None

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
            b_id, b_url = await self._process_bookmark(bookmark, i, total_bookmarks)
            if b_id:
                if "[WARNING]" not in b_url:
                    broken_ids.append(b_id)
                to_export.append((b_id, b_url))

            # Rate limit mitigation: sleep between checks
            if i < total_bookmarks:
                await asyncio.sleep(0.5 + random.uniform(0, 1.0))

        # Save learned rules
        self.history_manager.save()

        if self.export_file:
            self._export_results(to_export)

        if not self.dry_run and broken_ids:
            print(f"\nMoving {len(broken_ids)} broken bookmarks to trash...")
            self.client.move_to_trash_batch(broken_ids)
            self.results["moved"] = len(broken_ids)

        self._print_summary()

    async def run_recheck(self, recheck_file: str):
        """Re-check bookmarks listed in a file."""
        print(f"Re-checking bookmarks from {recheck_file}...")
        ids = []
        try:
            with open(recheck_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("\t")
                    try:
                        # Extract ID, ignore [WARNING] prefix if present in URL part
                        ids.append(int(parts[0]))
                    except ValueError:
                        print(f"Skipping invalid line: {line}")
        except FileNotFoundError:
            print(f"Error: File {recheck_file} not found.")
            return

        if not ids:
            print("No IDs found to re-check.")
            return

        total = len(ids)
        self.results["total"] = total
        to_export = []
        broken_ids = []

        for i, b_id in enumerate(ids, 1):
            bookmark = self.client.get_bookmark(b_id)
            if not bookmark:
                print(f"\n[Error] Could not fetch bookmark ID {b_id}. It might have been deleted.")
                continue

            res_id, res_url = await self._process_bookmark(bookmark, i, total)
            if res_id:
                if "[WARNING]" not in res_url:
                    broken_ids.append(res_id)
                to_export.append((res_id, res_url))

            if i < total:
                await asyncio.sleep(0.5 + random.uniform(0, 1.0))

        self.history_manager.save()

        if self.export_file:
            self._export_results(to_export)

        if not self.dry_run and broken_ids:
            print(f"\nMoving {len(broken_ids)} broken bookmarks to trash...")
            self.client.move_to_trash_batch(broken_ids)
            self.results["moved"] = len(broken_ids)

        self._print_summary()

    def _export_results(self, to_export):
        print(f"\nExporting {len(to_export)} items to {self.export_file}...")
        with open(self.export_file, "w") as f:
            for b_id, b_url in to_export:
                f.write(f"{b_id}\t{b_url}\n")

    def _print_summary(self):
        print("\n\nProcessing complete.")
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
