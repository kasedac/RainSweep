import pytest
import respx
from httpx import Response
from rainsweep.checker import LinkChecker


@pytest.mark.asyncio
async def test_is_broken_returns_false_for_successful_link():
    url = "https://example.com"
    async with respx.mock:
        respx.head(url).mock(return_value=Response(200))
        checker = LinkChecker()
        result = await checker.is_broken(url)
        assert result is False


@pytest.mark.asyncio
async def test_is_broken_retries_once_and_returns_false_if_second_attempt_succeeds(
    mocker,
):
    url = "https://example.com"
    # Use mocker to patch asyncio.sleep to avoid waiting in tests
    mocker.patch("asyncio.sleep", return_value=None)

    async with respx.mock:
        # First attempt: HEAD fails (500), then GET fails (500)
        # Second attempt: HEAD fails (500), then GET succeeds (200)
        head_route = respx.head(url)
        head_route.side_effect = [Response(500), Response(500)]

        get_route = respx.get(url)
        get_route.side_effect = [Response(500), Response(200)]

        checker = LinkChecker()
        result = await checker.is_broken(url)

        assert result is False
        assert head_route.call_count == 2
        assert get_route.call_count == 2


@pytest.mark.asyncio
async def test_is_broken_returns_true_if_all_attempts_fail(mocker):
    url = "https://example.com"
    mocker.patch("asyncio.sleep", return_value=None)

    async with respx.mock:
        # All 3 attempts fail
        head_route = respx.head(url).mock(return_value=Response(500))
        get_route = respx.get(url).mock(return_value=Response(500))

        checker = LinkChecker()
        result = await checker.is_broken(url)

        assert result is True
        assert head_route.call_count == 3
        assert get_route.call_count == 3


@pytest.mark.asyncio
async def test_is_broken_handles_429_with_longer_sleep(mocker):
    url = "https://example.com"
    sleep_mock = mocker.patch("asyncio.sleep", return_value=None)

    async with respx.mock:
        # First attempt: HEAD 429 -> fallback to GET 429 -> sleep 10
        # Second attempt: HEAD 200 -> return False
        head_route = respx.head(url)
        head_route.side_effect = [Response(429), Response(200)]

        get_route = respx.get(url)
        get_route.side_effect = [Response(429)]

        checker = LinkChecker()
        result = await checker.is_broken(url)

        assert result is False
        assert head_route.call_count == 2
        assert get_route.call_count == 1
        # Should have slept 10s after 429
        sleep_mock.assert_any_call(10)
