from unittest.mock import patch

import pytest

from word_chain_server.game_manager import GameManager


@pytest.fixture(scope='function')
@patch('word_chain_server.game_manager.GameManager.read_words_dictionary')
def game_manager(read_words_dictionary):
    game_manager = GameManager('')
    game_manager.words_with_scores = {'yes': 5, 'tests': 6}
    game_manager.words = {'y': ['yes'], 't': ['tests']}
    game_manager.diff = {"email_address": 1}
    return game_manager
