import asyncio
import datetime
import json
from collections import OrderedDict, defaultdict

from word_chain_server.consts import TIMEOUT, VOWEL_LIST

lock = asyncio.Lock()


class GameManager:
    def __init__(self, path):
        self.games = dict()
        self.timestamps = dict()
        self.games_history = dict()
        self.words = defaultdict(list)
        self.words_with_scores = dict()
        self.read_words_dictionary(path)

    def read_words_dictionary(self, path):
        with open(path, 'r') as json_file:
            words = json.load(json_file)
        for word in words:
            score = 0
            self.words[word[0]].append(word)
            for letter in word:
                if letter in VOWEL_LIST:
                    score += 2
                else:
                    score += 1
            self.words_with_scores[word] = score

    async def add_game(self, email_address, game_id):
        await lock.acquire()
        try:
            self.games[email_address] = game_id
            self.games_history[email_address] = OrderedDict()
        finally:
            lock.release()
        print(f'New game {game_id}. User {email_address}')

    async def check_word(self, email_address, word):
        await lock.acquire()
        res = True
        try:
            if word in self.games_history[email_address]:
                return False
            if word not in self.words_with_scores.keys():
                return False
            self.timestamps[email_address] = datetime.datetime.now()
            self.games_history[email_address][word] = None
        finally:
            lock.release()
        return res

    async def check_timeout(self, email_address):
        timestamp = await self.get_timestamp(email_address)
        now = datetime.datetime.now()
        if (now - timestamp).total_seconds() > TIMEOUT:
            return False
        return True

    async def get_timestamp(self, email_address):
        await lock.acquire()
        try:
            if email_address not in self.timestamps:
                self.timestamps[email_address] = datetime.datetime.now()
            timestamp = self.timestamps[email_address]
        finally:
            lock.release()
        return timestamp

    async def get_last_response(self, email_address):
        await lock.acquire()
        try:
            word = next(reversed(self.games_history[email_address]))
        finally:
            lock.release()
        return word
