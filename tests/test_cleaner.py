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


@pytest.mark.asyncio
async def test_cleaner_export(mock_client, mock_checker, tmp_path):
    export_file = tmp_path / "broken.tsv"

    bookmark1 = MagicMock()
    bookmark1.link = "http://example.com/ok"
    bookmark1._id = 1

    bookmark2 = MagicMock()
    bookmark2.link = "http://example.com/broken"
    bookmark2._id = 2

    mock_client.get_all_bookmarks.return_value = [bookmark1, bookmark2]
    mock_checker.is_broken.side_effect = [False, True]

    with patch("asyncio.sleep", new_callable=AsyncMock):
        cleaner = Cleaner(
            mock_client, mock_checker, dry_run=True, export_file=str(export_file)
        )
        await cleaner.run()

    assert export_file.exists()
    content = export_file.read_text()
    assert content == "2\thttp://example.com/broken\n"


@pytest.mark.asyncio
async def test_cleaner_import(mock_client, mock_checker, tmp_path):
    import_file = tmp_path / "import.tsv"
    import_file.write_text("10\thttp://example.com/old\n20\thttp://example.com/dead\n")

    cleaner = Cleaner(mock_client, mock_checker)
    await cleaner.run_import(str(import_file))

    summary = cleaner.get_summary()
    assert summary["broken"] == 2
    assert summary["moved"] == 2

    # Ensure move_to_trash_batch was called with the imported IDs
    mock_client.move_to_trash_batch.assert_called_once_with([10, 20])


@pytest.mark.asyncio
async def test_cleaner_import_invalid_lines(mock_client, mock_checker, tmp_path):
    import_file = tmp_path / "invalid.tsv"
    import_file.write_text("10\tok\nnot_an_id\terror\n\n30\talso_ok\n")

    cleaner = Cleaner(mock_client, mock_checker)
    await cleaner.run_import(str(import_file))

    summary = cleaner.get_summary()
    assert summary["broken"] == 2
    assert summary["moved"] == 2

    # Should skip the line with "not_an_id" and the empty line
    mock_client.move_to_trash_batch.assert_called_once_with([10, 30])
