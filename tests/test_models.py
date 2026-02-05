import pytest

from ambient_mcp.models import GetDataInput


def test_get_data_input_requires_from_and_to_together() -> None:
    with pytest.raises(ValueError, match="'from' and 'to' must be provided together"):
        GetDataInput.model_validate(
            {
                "read_key": "abc",
                "channel_id": 1,
                "from": "2024-01-01T00:00:00Z",
            }
        )

    with pytest.raises(ValueError, match="'from' and 'to' must be provided together"):
        GetDataInput.model_validate(
            {
                "read_key": "abc",
                "channel_id": 1,
                "to": "2024-01-01T00:00:00Z",
            }
        )


def test_get_data_input_requires_n_when_skip_is_present() -> None:
    with pytest.raises(ValueError, match="'skip' requires 'n'"):
        GetDataInput.model_validate(
            {
                "read_key": "abc",
                "channel_id": 1,
                "skip": 1,
            }
        )


def test_get_data_input_disallows_from_to_with_n_or_skip() -> None:
    with pytest.raises(ValueError, match="Use either 'from/to' or 'n/skip', not both"):
        GetDataInput.model_validate(
            {
                "read_key": "abc",
                "channel_id": 1,
                "from": "2024-01-01T00:00:00Z",
                "to": "2024-01-01T00:10:00Z",
                "n": 5,
            }
        )


def test_get_data_input_requires_any_time_or_count() -> None:
    with pytest.raises(ValueError, match="Either 'from/to' or 'n' must be provided"):
        GetDataInput.model_validate(
            {
                "read_key": "abc",
                "channel_id": 1,
            }
        )


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (
            {
                "read_key": "abc",
                "channel_id": 1,
                "from": "2024-01-01T00:00:00Z",
                "to": "2024-01-01T00:05:00Z",
            },
            ("2024-01-01T00:00:00Z", "2024-01-01T00:05:00Z", None, None),
        ),
        (
            {
                "read_key": "abc",
                "channel_id": 1,
                "n": 10,
                "skip": 2,
            },
            (None, None, 10, 2),
        ),
    ],
)
def test_get_data_input_accepts_valid_payloads(
    payload: dict[str, object],
    expected: tuple[str | None, str | None, int | None, int | None],
) -> None:
    model = GetDataInput.model_validate(payload)
    assert (model.from_, model.to, model.n, model.skip) == expected
