import os
import time
from typing import List, Optional
from raindropiopy.api import API
from raindropiopy.models import Raindrop, CollectionRef, URL


class RaindropClient:
    """Client to interact with Raindrop.io API."""

    def __init__(
        self, token: Optional[str] = None, token_env_var: str = "RAINDROP_TOKEN"
    ):
        """Initialize the client with a token or from an environment variable."""
        if not token:
            token = os.environ.get(token_env_var)

        if not token:
            raise ValueError(
                f"Token not provided and environment variable '{token_env_var}' is not set."
            )
        self.api = API(token=token)

    def get_all_bookmarks(self) -> List[Raindrop]:
        """Fetch all bookmarks across all pages."""
        page = 0
        all_bookmarks = []
        while True:
            # Retry mechanism for search_paged
            bookmarks = None
            for attempt in range(3):
                try:
                    bookmarks = Raindrop._search_paged(self.api, page=page, perpage=50)
                    break
                except Exception as e:
                    if attempt == 2:
                        raise
                    error_msg = str(e)
                    if any(code in error_msg for code in ["502", "503", "504"]):
                        time.sleep(2**attempt)
                        continue
                    raise

            if not bookmarks:
                break
            all_bookmarks.extend(bookmarks)
            page += 1
        return all_bookmarks

    def move_to_trash(self, bookmark_id: int):
        """Move a bookmark to the trash (System collection -99)."""
        Raindrop.update(self.api, id=bookmark_id, collection=CollectionRef.Trash.id)

    def move_to_trash_batch(self, ids: list[int]):
        """Move multiple bookmarks to the trash."""
        if not ids:
            return
        url = URL.format(path="raindrops/0")

        # Retry mechanism for batch update
        for attempt in range(3):
            try:
                self.api.put(url, json={"ids": ids, "collection": {"$id": -99}})
                break
            except Exception as e:
                if attempt == 2:
                    raise
                error_msg = str(e)
                if any(code in error_msg for code in ["502", "503", "504"]):
                    time.sleep(2**attempt)
                    continue
                raise
