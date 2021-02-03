import pytest


@pytest.mark.asyncio
async def test_add_game(game_manager):
    msg = await game_manager.add_game("email_address", "game_id")
    assert msg == 'New game game_id. User email_address'


@pytest.mark.asyncio
async def test_add_game_for_two_users_twice(game_manager):
    msg = await game_manager.add_game("email_address", "game_id")
    assert msg == 'New game game_id. User email_address'
    msg = await game_manager.add_game("email_address", "game_id2")
    assert msg == 'Reset game for user email_address'


@pytest.mark.asyncio
async def test_check_word_new_word(game_manager):
    msg = await game_manager.add_game("email_address", "game_id")
    assert msg == 'New game game_id. User email_address'
    assert await game_manager.check_word("email_address", "yes")
    assert game_manager.scores["email_address"] == [7.5, 0]


@pytest.mark.asyncio
async def test_check_add_same_word_twice(game_manager):
    msg = await game_manager.add_game("email_address", "game_id")
    assert msg == 'New game game_id. User email_address'
    assert await game_manager.check_word("email_address", "yes")
    assert game_manager.scores["email_address"] == [7.5, 0]
    assert not await game_manager.check_word("email_address", "yes")
    assert game_manager.scores["email_address"] == [7.5, 0]


@pytest.mark.asyncio
async def test_check_word_score_without_bonus(game_manager):
    game_manager.diff = {"email_address": 18}
    msg = await game_manager.add_game("email_address", "game_id")
    assert msg == 'New game game_id. User email_address'
    assert await game_manager.check_word("email_address", "yes")
    assert game_manager.scores["email_address"] == [5, 0]


@pytest.mark.asyncio
async def test_reset(game_manager):
    msg = await game_manager.add_game("email_address", "game_id")
    assert msg == 'New game game_id. User email_address'
    assert await game_manager.check_word("email_address", "yes")
    assert game_manager.scores["email_address"] == [7.5, 0]
    await game_manager.reset("email_address")
    with pytest.raises(KeyError):
        assert not await game_manager.check_word("email_address", "tests")
    # add the same user after reset
    msg = await game_manager.add_game("email_address", "game_id")
    # add the same word after reset
    assert await game_manager.check_word("email_address", "yes")
    assert game_manager.scores["email_address"] == [7.5, 0]


@pytest.mark.asyncio
async def test_check_word_invalid(game_manager):
    msg = await game_manager.add_game("email_address", "game_id")
    assert msg == 'New game game_id. User email_address'
    assert not await game_manager.check_word("email_address", "invalid")
    assert game_manager.scores["email_address"] == [0, 0]
