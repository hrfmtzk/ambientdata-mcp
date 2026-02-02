import pytest
from pytest_mock import MockFixture

from ambientdata_mcp.client import ApiResponse
from ambientdata_mcp.models import GetDataErrorOutput, GetDataInput, GetDataOutput
from ambientdata_mcp.server import get_data


class DummyContext:
    async def info(self, _: str) -> None:
        return None

    async def debug(self, _: str) -> None:
        return None

    async def error(self, _: str) -> None:
        return None


@pytest.mark.asyncio
async def test_get_data_returns_error_output(mocker: MockFixture) -> None:
    params = GetDataInput.model_validate(
        {
            "read_key": "key",
            "channel_id": 1,
            "n": 1,
        }
    )
    context = DummyContext()

    mocker.patch(
        "ambientdata_mcp.server.AmbientClient.get_channel_properties",
        return_value=ApiResponse(status_code=200, payload={}, raw_body=""),
    )
    mocker.patch(
        "ambientdata_mcp.server.AmbientClient.get_data",
        return_value=ApiResponse(status_code=500, payload={}, raw_body=""),
    )
    mocker.patch(
        "ambientdata_mcp.server.build_error_output",
        return_value=GetDataErrorOutput(category="upstream", message="boom"),
    )

    result = await get_data(params, context)

    assert isinstance(result, GetDataErrorOutput)
    assert result.category == "upstream"
    assert result.message == "boom"


@pytest.mark.asyncio
async def test_get_data_returns_success_output(mocker: MockFixture) -> None:
    params = GetDataInput.model_validate(
        {
            "read_key": "key",
            "channel_id": 1,
            "n": 1,
        }
    )
    context = DummyContext()

    mocker.patch(
        "ambientdata_mcp.server.AmbientClient.get_channel_properties",
        return_value=ApiResponse(
            status_code=200,
            payload={"d1": {"name": "temperature"}},
            raw_body="",
        ),
    )
    mocker.patch(
        "ambientdata_mcp.server.AmbientClient.get_data",
        return_value=ApiResponse(
            status_code=200,
            payload=[{"created": "2024-01-01T00:00:00Z", "d1": 1}],
            raw_body="",
        ),
    )
    mocker.patch("ambientdata_mcp.server.build_error_output", return_value=None)

    result = await get_data(params, context)

    assert isinstance(result, GetDataOutput)
    assert result.field_labels.d1 == "temperature"
    assert result.items[0].d1 == 1


@pytest.mark.asyncio
async def test_get_data_returns_validation_error_on_exception(
    mocker: MockFixture,
) -> None:
    params = GetDataInput.model_validate(
        {
            "read_key": "key",
            "channel_id": 1,
            "n": 1,
        }
    )
    context = DummyContext()

    mocker.patch(
        "ambientdata_mcp.server.AmbientClient.get_channel_properties",
        side_effect=RuntimeError("broken"),
    )

    result = await get_data(params, context)

    assert isinstance(result, GetDataErrorOutput)
    assert result.category == "validation"
    assert "broken" in result.message
