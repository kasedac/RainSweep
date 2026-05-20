import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from rainsweep.cleaner import Cleaner
from rainsweep.client import RaindropClient
from rainsweep.checker import LinkChecker


@pytest.fixture
def mock_client():
    client = MagicMock(spec=RaindropClient)
    return client


@pytest.fixture
def mock_checker():
    checker = MagicMock(spec=LinkChecker)
    checker.is_broken = AsyncMock()
    return checker


@pytest.mark.asyncio
async def test_cleaner_dry_run(mock_client, mock_checker):
    # Setup mock bookmarks
    bookmark1 = MagicMock()
    bookmark1.link = "http://example.com/ok"
    bookmark1._id = 1

    bookmark2 = MagicMock()
    bookmark2.link = "http://example.com/broken"
    bookmark2._id = 2

    mock_client.get_all_bookmarks.return_value = [bookmark1, bookmark2]

    # Mock checker results
    mock_checker.is_broken.side_effect = [False, True]

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        cleaner = Cleaner(mock_client, mock_checker, dry_run=True)
        await cleaner.run()
        assert mock_sleep.call_count == 1  # Called between checks

    summary = cleaner.get_summary()
    assert summary["total"] == 2
    assert summary["broken"] == 1
    assert summary["moved"] == 0

    # Ensure move_to_trash_batch was NOT called in dry-run
    mock_client.move_to_trash_batch.assert_not_called()


@pytest.mark.asyncio
async def test_cleaner_real_run(mock_client, mock_checker):
    # Setup mock bookmarks
    bookmark1 = MagicMock()
    bookmark1.link = "http://example.com/ok"
    bookmark1._id = 1

    bookmark2 = MagicMock()
    bookmark2.link = "http://example.com/broken"
    bookmark2._id = 2

    mock_client.get_all_bookmarks.return_value = [bookmark1, bookmark2]

    # Mock checker results
    mock_checker.is_broken.side_effect = [False, True]

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        cleaner = Cleaner(mock_client, mock_checker, dry_run=False)
        await cleaner.run()
        assert mock_sleep.call_count == 1

    summary = cleaner.get_summary()
    assert summary["total"] == 2
    assert summary["broken"] == 1
    assert summary["moved"] == 1

    # Ensure move_to_trash_batch was called for the broken bookmark
    mock_client.move_to_trash_batch.assert_called_once_with([2])
