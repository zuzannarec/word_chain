import pytest

from word_chain_server.utils import get_name_by_id


@pytest.mark.asyncio
async def test_id_name_map():
    result = await get_name_by_id("1")
    assert result == "Zuzanna"
