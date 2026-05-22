import pytest
import respx
from httpx import Response
from rainsweep.checker import LinkChecker, LinkStatus


@pytest.mark.asyncio
async def test_check_link_returns_alive_for_successful_link():
    url = "https://example.com"
    async with respx.mock:
        respx.head(url).mock(return_value=Response(200))
        checker = LinkChecker()
        status, reason, worked_ua = await checker.check_link(url)
        assert status == LinkStatus.ALIVE
        assert reason == "OK"
        assert worked_ua == "browser"


@pytest.mark.asyncio
async def test_check_link_retries_once_and_returns_alive_if_second_attempt_succeeds(
    mocker,
):
    url = "https://example.com"
    # Use mocker to patch asyncio.sleep to avoid waiting in tests
    mocker.patch("asyncio.sleep", return_value=None)

    async with respx.mock:
        # First attempt: HEAD fails (500), then GET fails (500)
        # Second attempt: HEAD succeeds (200)
        head_route = respx.head(url)
        head_route.side_effect = [Response(500), Response(200)]

        get_route = respx.get(url)
        get_route.side_effect = [Response(500)]

        checker = LinkChecker()
        status, reason, worked_ua = await checker.check_link(url)

        assert status == LinkStatus.ALIVE
        assert reason == "OK"
        assert worked_ua == "browser"
        assert head_route.call_count == 2
        assert get_route.call_count == 1


@pytest.mark.asyncio
async def test_check_link_returns_broken_for_404(mocker):
    url = "https://example.com"
    mocker.patch("asyncio.sleep", return_value=None)

    async with respx.mock:
        respx.head(url).mock(return_value=Response(404))
        respx.get(url).mock(return_value=Response(404))

        checker = LinkChecker()
        status, reason, worked_ua = await checker.check_link(url)

        assert status == LinkStatus.BROKEN
        assert "Status 404" in reason
        assert worked_ua is None


@pytest.mark.asyncio
async def test_check_link_returns_warning_for_500_after_retries(mocker):
    url = "https://example.com"
    mocker.patch("asyncio.sleep", return_value=None)

    async with respx.mock:
        # All 3 attempts fail with 500
        respx.head(url).mock(return_value=Response(500))
        respx.get(url).mock(return_value=Response(500))

        checker = LinkChecker()
        status, reason, worked_ua = await checker.check_link(url)

        assert status == LinkStatus.WARNING
        assert "Status 500" in reason


@pytest.mark.asyncio
async def test_check_link_handles_429_with_ua_switch(mocker):
    url = "https://example.com"
    sleep_mock = mocker.patch("asyncio.sleep", return_value=None)

    async with respx.mock:
        # 1st attempt: HEAD browser UA -> 429
        #   Sleeps, switches to default UA
        # 2nd attempt: HEAD default UA -> 200

        head_route = respx.head(url)
        head_route.side_effect = [
            Response(429),  # 1st attempt, browser UA
            Response(200),  # 2nd attempt, default UA
        ]

        checker = LinkChecker()
        status, reason, worked_ua = await checker.check_link(url)

        assert status == LinkStatus.ALIVE
        assert worked_ua == "default"
        assert head_route.call_count == 2
        # Should have slept after 429
        sleep_mock.assert_any_call(5)


@pytest.mark.asyncio
async def test_check_link_preferred_ua_default(mocker):
    url = "https://hatena.blog/user/entry"
    mocker.patch("asyncio.sleep", return_value=None)

    async with respx.mock:
        # Should start with default UA immediately
        head_route = respx.head(url).mock(return_value=Response(200))

        checker = LinkChecker()
        status, reason, worked_ua = await checker.check_link(url, preferred_ua="default")

        assert status == LinkStatus.ALIVE
        assert worked_ua == "default"
        # Check UA used in the request
        last_request = head_route.calls.last.request
        assert "Chrome" not in last_request.headers.get("User-Agent", "")
