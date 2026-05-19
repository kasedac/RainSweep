import os
from typing import List, Optional
from raindropiopy.api import API
from raindropiopy.models import Raindrop, CollectionRef


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
            bookmarks = Raindrop._search_paged(self.api, page=page, perpage=50)
            if not bookmarks:
                break
            all_bookmarks.extend(bookmarks)
            page += 1
        return all_bookmarks

    def move_to_trash(self, bookmark_id: int):
        """Move a bookmark to the trash (System collection -99)."""
        Raindrop.update(self.api, id=bookmark_id, collection=CollectionRef.Trash.id)
