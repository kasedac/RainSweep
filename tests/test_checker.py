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
        is_broken, reason = await checker.is_broken(url)
        assert is_broken is False
        assert reason == "OK"


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
        is_broken, reason = await checker.is_broken(url)

        assert is_broken is False
        assert reason == "OK"
        # Since HEAD 500 doesn't trigger adaptive UA, we have 2 attempts
        assert head_route.call_count == 2
        assert get_route.call_count == 2


@pytest.mark.asyncio
async def test_is_broken_returns_true_if_all_attempts_fail(mocker):
    url = "https://example.com"
    mocker.patch("asyncio.sleep", return_value=None)

    async with respx.mock:
        # All 3 attempts fail (max_attempts = 3)
        head_route = respx.head(url).mock(return_value=Response(500))
        get_route = respx.get(url).mock(return_value=Response(500))

        checker = LinkChecker()
        is_broken, reason = await checker.is_broken(url)

        assert is_broken is True
        assert "Status 500" in reason
        assert head_route.call_count == 3
        assert get_route.call_count == 3


@pytest.mark.asyncio
async def test_is_broken_handles_429_with_longer_sleep(mocker):
    url = "https://example.com"
    sleep_mock = mocker.patch("asyncio.sleep", return_value=None)

    async with respx.mock:
        # First attempt:
        #   HEAD Chrome UA -> 429
        #   HEAD Default UA -> 429
        #   Sleep base_delay * 2^0 = 5
        # Second attempt:
        #   HEAD Default UA -> 200

        head_route = respx.head(url)
        head_route.side_effect = [
            Response(429),  # 1st attempt, Chrome UA
            Response(429),  # 1st attempt, Default UA retry
            Response(200),  # 2nd attempt, Default UA
        ]

        checker = LinkChecker()
        is_broken, reason = await checker.is_broken(url)

        assert is_broken is False
        assert reason == "OK"
        assert head_route.call_count == 3
        # Should have slept 5s after both UA retries failed with 429
        sleep_mock.assert_any_call(5)


@pytest.mark.asyncio
async def test_is_broken_hatena_behavior_fallback_to_default_ua(mocker):
    url = "https://hatena.blog/user/entry"
    mocker.patch("asyncio.sleep", return_value=None)

    async with respx.mock:
        # Mock behavior:
        # Chrome UA -> 429
        # Default UA -> 200
        def hatena_side_effect(request):
            ua = request.headers.get("User-Agent", "")
            if "Chrome" in ua:
                return Response(429)
            return Response(200)

        respx.head(url).side_effect = hatena_side_effect

        checker = LinkChecker()
        is_broken, reason = await checker.is_broken(url)

        assert is_broken is False
        assert reason == "OK"


@pytest.mark.asyncio
async def test_is_broken_wikipedia_behavior_chrome_ua_succeeds(mocker):
    url = "https://wikipedia.org/wiki/Main_Page"
    mocker.patch("asyncio.sleep", return_value=None)

    async with respx.mock:
        # Mock behavior:
        # Default UA (no Chrome) -> 403
        # Chrome UA -> 200
        def wikipedia_side_effect(request):
            ua = request.headers.get("User-Agent", "")
            if "Chrome" in ua:
                return Response(200)
            return Response(403)

        respx.head(url).side_effect = wikipedia_side_effect

        checker = LinkChecker()
        # Ensure we start with browser headers
        is_broken, reason = await checker.is_broken(url)

        assert is_broken is False
        assert reason == "OK"
