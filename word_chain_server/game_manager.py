import asyncio
import datetime
import json
from collections import OrderedDict, defaultdict
from random import random

from word_chain_server.consts import TIMEOUT, VOWEL_LIST, BONUS_TIME, BONUS

lock = asyncio.Lock()


class GameManager:
    def __init__(self, path):
        self.games = dict()
        self.timestamps = dict()
        self.games_history = dict()
        self.words = defaultdict(list)
        self.words_with_scores = dict()
        self.read_words_dictionary(path)
        self.scores = dict()
        self.diff = dict()

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
        msg = f'New game {game_id}. User {email_address}'
        await lock.acquire()  # lock is needed to guarantee exclusive access to a shared resources for the coroutine
        try:
            if email_address in self.games.keys():
                msg = f'Reset game for user {email_address}'
            self.games[email_address] = game_id
            self.games_history[email_address] = OrderedDict()
            self.scores[email_address] = [0, 0]
        finally:
            lock.release()
        return msg

    async def check_word(self, email_address, word):
        await lock.acquire()
        try:
            if word in self.games_history[email_address]:
                return False
            if word not in self.words_with_scores.keys():
                return False
            last_word = self._get_last_response(email_address)
            if last_word is not None:
                if word[0] != last_word[-1]:
                    return False
            user_score = self.words_with_scores[word]
            if self.diff[email_address] < BONUS_TIME:
                user_score = user_score * BONUS
            self._update_scores(email_address, score_user=user_score)
            self.timestamps[email_address] = datetime.datetime.now()
            self.games_history[email_address][word] = None
        finally:
            lock.release()
        return True

    async def get_computer_response(self, email_address, word):
        await lock.acquire()
        try:
            possible_words = self.words[word[-1]]
            result_word = random.choice(possible_words)
            computer_score = self.words_with_scores[result_word]
            self.games_history[email_address][result_word] = None
            scores = self._update_scores(email_address, score_computer=computer_score)
        finally:
            lock.release()
        return result_word, scores

    async def check_user(self, email_address):
        await lock.acquire()
        try:
            if email_address not in self.games:
                return False
            return True
        finally:
            lock.release()

    async def check_timeout(self, email_address):
        timestamp = await self.get_timestamp(email_address)
        now = datetime.datetime.now()
        diff = (now - timestamp).total_seconds()
        if diff > TIMEOUT:
            return False
        await self.update_diff(email_address, diff)
        return True

    async def update_diff(self, email_address, diff):
        await lock.acquire()
        try:
            self.diff[email_address] = diff
        finally:
            lock.release()

    async def get_timestamp(self, email_address):
        await lock.acquire()
        try:
            if email_address not in self.timestamps:
                self.timestamps[email_address] = datetime.datetime.now()
            timestamp = self.timestamps[email_address]
        finally:
            lock.release()
        return timestamp

    async def get_history(self, email_address):
        await lock.acquire()
        try:
            return list(self.games_history[email_address].keys())
        finally:
            lock.release()

    async def get_scores(self, email_address):
        await lock.acquire()
        try:
            return self.scores[email_address]
        finally:
            lock.release()

    async def reset(self, email_address):
        await lock.acquire()
        try:
            del self.games[email_address]
            del self.games_history[email_address]
            del self.scores[email_address]
            del self.timestamps[email_address]
        finally:
            lock.release()

    def _get_last_response(self, email_address):
        try:
            word = next(reversed(self.games_history[email_address]))
        except StopIteration:
            return None
        return word

    def _update_scores(self, email_address, score_user=0, score_computer=0):
        scores = self.scores[email_address]
        score_user = scores[0] + score_user
        score_computer = scores[1] + score_computer
        self.scores[email_address] = [score_user, score_computer]
        return scores

    def _check_computer_word(self, email_address, word):
        if word in self.games_history[email_address]:
            return False
        return True
