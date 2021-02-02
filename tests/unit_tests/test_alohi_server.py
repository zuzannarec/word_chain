import pytest

from alohi_server.fast_api_server import get_name_by_id


@pytest.mark.asyncio
async def test_id_name_map():
    result = await get_name_by_id("1")
    assert result == "Zuzanna"
