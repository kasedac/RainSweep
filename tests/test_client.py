import pytest
from unittest.mock import MagicMock, patch
from rainsweep.client import RaindropClient


@pytest.fixture
def raindrop_client(monkeypatch):
    monkeypatch.setenv("RAINDROP_TOKEN", "fake_token")
    # API instance is created during __init__
    with patch("rainsweep.client.API"):
        client = RaindropClient()
        yield client


def test_init_uses_env_token(monkeypatch):
    monkeypatch.setenv("RAINDROP_TOKEN", "test_token")
    with patch("rainsweep.client.API") as mock_api_class:
        RaindropClient()
        mock_api_class.assert_called_once_with(token="test_token")


def test_init_uses_custom_env_var(monkeypatch):
    monkeypatch.setenv("CUSTOM_TOKEN", "custom_test_token")
    with patch("rainsweep.client.API") as mock_api_class:
        RaindropClient(token_env_var="CUSTOM_TOKEN")
        mock_api_class.assert_called_once_with(token="custom_test_token")


def test_get_all_bookmarks(raindrop_client):
    with patch("rainsweep.client.Raindrop._search_paged") as mock_search_paged:
        # Mocking 2 pages of results
        mock_search_paged.side_effect = [
            [MagicMock(), MagicMock()],  # Page 0
            [MagicMock()],  # Page 1
            [],  # Page 2 (end)
        ]
        bookmarks = raindrop_client.get_all_bookmarks()

        assert len(bookmarks) == 3
        assert mock_search_paged.call_count == 3
        mock_search_paged.assert_any_call(raindrop_client.api, page=0, perpage=50)
        mock_search_paged.assert_any_call(raindrop_client.api, page=1, perpage=50)
        mock_search_paged.assert_any_call(raindrop_client.api, page=2, perpage=50)


def test_move_to_trash(raindrop_client):
    from raindropiopy.models import CollectionRef

    with patch("rainsweep.client.Raindrop.update") as mock_update:
        raindrop_client.move_to_trash(12345)
        mock_update.assert_called_once_with(
            raindrop_client.api, id=12345, collection=CollectionRef.Trash.id
        )
