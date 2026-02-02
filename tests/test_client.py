import json

import pytest
import respx
from httpx import Response

from ambientdata_mcp.client import AmbientClient


@pytest.mark.asyncio
async def test_get_channel_properties_parses_json_payload() -> None:
    client = AmbientClient(channel_id=1, read_key="key", base_url="https://example.com")
    async with respx.mock(base_url="https://example.com") as router:
        route = router.get("/channels/1").mock(
            return_value=Response(200, json={"ok": True})
        )
        response = await client.get_channel_properties()

    assert route.called
    assert response.status_code == 200
    assert response.payload == {"ok": True}


@pytest.mark.asyncio
async def test_get_data_handles_non_json_body() -> None:
    client = AmbientClient(channel_id=1, read_key="key", base_url="https://example.com")
    async with respx.mock(base_url="https://example.com") as router:
        router.get("/channels/1/data").mock(return_value=Response(500, text="oops"))
        response = await client.get_data(from_=None, to=None, n=1, skip=None)

    assert response.status_code == 500
    assert response.payload is None
    assert response.raw_body == "oops"


@pytest.mark.asyncio
async def test_get_data_includes_query_params() -> None:
    client = AmbientClient(channel_id=2, read_key="key", base_url="https://example.com")
    async with respx.mock(base_url="https://example.com") as router:
        route = router.get("/channels/2/data").mock(
            return_value=Response(200, text=json.dumps([]))
        )
        response = await client.get_data(
            from_="2024-01-01T00:00:00Z",
            to="2024-01-01T00:05:00Z",
            n=None,
            skip=None,
        )

    assert route.called
    request = route.calls[0].request
    assert response.status_code == 200
    assert request.url.params["readKey"] == "key"
    assert request.url.params["start"] == "2024-01-01T00:00:00Z"
    assert request.url.params["end"] == "2024-01-01T00:05:00Z"
