from unittest.mock import patch

import pytest

from word_chain_server.game_manager import GameManager


@pytest.mark.asyncio
@patch('word_chain_server.game_manager.GameManager.read_words_dictionary')
async def test_add_game(read_words_dictionary):
    game_manager = GameManager("")
    msg = await game_manager.add_game("email_address", "game_id")
    assert msg == 'New game game_id. User email_address'


@pytest.mark.asyncio
@patch('word_chain_server.game_manager.GameManager.read_words_dictionary')
async def test_add_game_for_two_users_twice(read_words_dictionary):
    game_manager = GameManager("")
    msg = await game_manager.add_game("email_address", "game_id")
    assert msg == 'New game game_id. User email_address'
    msg = await game_manager.add_game("email_address", "game_id2")
    assert msg == 'Reset game for user email_address'


@pytest.mark.asyncio
@patch('word_chain_server.game_manager.GameManager.read_words_dictionary')
async def test_check_word_new_word(read_words_dictionary):
    game_manager = GameManager("")
    game_manager.words_with_scores = {"yes": 5}
    game_manager.words = {"y": ["yes"]}
    game_manager.diff = {"email_address": 1}
    msg = await game_manager.add_game("email_address", "game_id")
    assert msg == 'New game game_id. User email_address'
    assert await game_manager.check_word("email_address", "yes")
    assert game_manager.scores["email_address"] == [7.5, 0]


@pytest.mark.asyncio
@patch('word_chain_server.game_manager.GameManager.read_words_dictionary')
async def test_check_add_same_word_twice(read_words_dictionary):
    game_manager = GameManager("")
    game_manager.words_with_scores = {"yes": 5}
    game_manager.words = {"y": ["yes"]}
    game_manager.diff = {"email_address": 1}
    msg = await game_manager.add_game("email_address", "game_id")
    assert msg == 'New game game_id. User email_address'
    assert await game_manager.check_word("email_address", "yes")
    assert game_manager.scores["email_address"] == [7.5, 0]
    assert not await game_manager.check_word("email_address", "yes")
    assert game_manager.scores["email_address"] == [7.5, 0]


@pytest.mark.asyncio
@patch('word_chain_server.game_manager.GameManager.read_words_dictionary')
async def test_check_word_score_without_bonus(read_words_dictionary):
    game_manager = GameManager("")
    game_manager.words_with_scores = {"yes": 5}
    game_manager.words = {"y": ["yes"]}
    game_manager.diff = {"email_address": 18}
    msg = await game_manager.add_game("email_address", "game_id")
    assert msg == 'New game game_id. User email_address'
    assert await game_manager.check_word("email_address", "yes")
    assert game_manager.scores["email_address"] == [5, 0]
