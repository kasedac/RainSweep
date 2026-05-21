import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from rainsweep.cleaner import Cleaner
from rainsweep.client import RaindropClient
from rainsweep.checker import LinkChecker, LinkStatus


@pytest.fixture
def mock_client():
    client = MagicMock(spec=RaindropClient)
    return client


@pytest.fixture
def mock_checker():
    checker = MagicMock(spec=LinkChecker)
    checker.check_link = AsyncMock()
    return checker


@pytest.mark.asyncio
async def test_cleaner_dry_run(mock_client, mock_checker):
    # Setup mock bookmarks
    bookmark1 = MagicMock()
    bookmark1.link = "http://example.com/ok"
    bookmark1.id = 1

    bookmark2 = MagicMock()
    bookmark2.link = "http://example.com/broken"
    bookmark2.id = 2

    mock_client.get_all_bookmarks.return_value = [bookmark1, bookmark2]

    # Mock checker results
    mock_checker.check_link.side_effect = [
        (LinkStatus.ALIVE, "OK"),
        (LinkStatus.BROKEN, "Status 404"),
    ]

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        cleaner = Cleaner(mock_client, mock_checker, dry_run=True)
        await cleaner.run()
        assert mock_sleep.call_count == 1  # Called between checks

    summary = cleaner.get_summary()
    assert summary["total"] == 2
    assert summary["broken"] == 1
    assert summary["warning"] == 0
    assert summary["moved"] == 0

    # Ensure move_to_trash_batch was NOT called in dry-run
    mock_client.move_to_trash_batch.assert_not_called()


@pytest.mark.asyncio
async def test_cleaner_real_run(mock_client, mock_checker):
    # Setup mock bookmarks
    bookmark1 = MagicMock()
    bookmark1.link = "http://example.com/ok"
    bookmark1.id = 1

    bookmark2 = MagicMock()
    bookmark2.link = "http://example.com/broken"
    bookmark2.id = 2

    mock_client.get_all_bookmarks.return_value = [bookmark1, bookmark2]

    # Mock checker results
    mock_checker.check_link.side_effect = [
        (LinkStatus.ALIVE, "OK"),
        (LinkStatus.BROKEN, "Status 404"),
    ]

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


@pytest.mark.asyncio
async def test_cleaner_with_warning(mock_client, mock_checker, tmp_path):
    # Setup mock bookmarks
    bookmark1 = MagicMock()
    bookmark1.link = "http://example.com/ok"
    bookmark1.id = 1

    bookmark2 = MagicMock()
    bookmark2.link = "http://example.com/warning"
    bookmark2.id = 2

    mock_client.get_all_bookmarks.return_value = [bookmark1, bookmark2]

    # Mock checker results
    mock_checker.check_link.side_effect = [
        (LinkStatus.ALIVE, "OK"),
        (LinkStatus.WARNING, "Status 403"),
    ]

    export_file = tmp_path / "warning_export.tsv"
    with patch("asyncio.sleep", new_callable=AsyncMock):
        cleaner = Cleaner(
            mock_client, mock_checker, dry_run=False, export_file=str(export_file)
        )
        await cleaner.run()

    summary = cleaner.get_summary()
    assert summary["total"] == 2
    assert summary["broken"] == 0
    assert summary["warning"] == 1
    assert summary["moved"] == 0

    # Ensure move_to_trash_batch was NOT called for warning
    mock_client.move_to_trash_batch.assert_not_called()

    # Check export content
    content = export_file.read_text()
    assert "2\t[WARNING] http://example.com/warning\n" in content


@pytest.mark.asyncio
async def test_cleaner_export(mock_client, mock_checker, tmp_path):
    export_file = tmp_path / "broken.tsv"

    bookmark1 = MagicMock()
    bookmark1.link = "http://example.com/ok"
    bookmark1.id = 1

    bookmark2 = MagicMock()
    bookmark2.link = "http://example.com/broken"
    bookmark2.id = 2

    mock_client.get_all_bookmarks.return_value = [bookmark1, bookmark2]
    mock_checker.check_link.side_effect = [
        (LinkStatus.ALIVE, "OK"),
        (LinkStatus.BROKEN, "Status 404"),
    ]

    with patch("asyncio.sleep", new_callable=AsyncMock):
        cleaner = Cleaner(
            mock_client, mock_checker, dry_run=True, export_file=str(export_file)
        )
        await cleaner.run()

    assert export_file.exists()
    content = export_file.read_text()
    assert content == "2\thttp://example.com/broken\n"


@pytest.mark.asyncio
async def test_cleaner_import_skips_warning(mock_client, mock_checker, tmp_path):
    import_file = tmp_path / "import_warn.tsv"
    import_file.write_text(
        "10\thttp://example.com/dead\n20\t[WARNING] http://example.com/suspicious\n30\thttp://example.com/gone\n"
    )

    cleaner = Cleaner(mock_client, mock_checker)
    await cleaner.run_import(str(import_file))

    summary = cleaner.get_summary()
    assert summary["broken"] == 2
    assert summary["moved"] == 2

    # Should skip ID 20 because of [WARNING]
    mock_client.move_to_trash_batch.assert_called_once_with([10, 30])
