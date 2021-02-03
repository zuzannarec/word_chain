import asyncio
from collections import OrderedDict

from word_chain_server.consts import TIMEOUT

lock = asyncio.Lock()


class GameManager:
    def __init__(self):
        self.games = dict()
        self.events = dict()
        self.games_history = dict()

    async def add_game(self, email_address, game_id):
        await lock.acquire()
        try:
            self.games[email_address] = game_id
            self.events[email_address] = asyncio.Event()
            self.games_history[email_address] = OrderedDict()
        finally:
            lock.release()
        print(f'New game {game_id}. User {email_address}')

    async def wait_for_users_response(self, email_address):
        print(f'Waiting for response of user {email_address}. Opponent word {self.games_history[email_address][-1]}')
        event = await self.get_event(email_address)
        event.clear()
        try:
            await asyncio.wait_for(event, timeout=TIMEOUT)
        except asyncio.TimeoutError:
            event.set()
            raise
        event.clear()
        word = await self.get_last_response(email_address)
        print(f'User {email_address} responded {word}.')

    async def set_event(self, email_address, word):
        event = await self.get_event(email_address)
        if event.is_set():
            event.clear()
            return False, 'Timeout. Game finished.'  # TODO return results, history
        if word in self.games_history[email_address]:
            return False, "Repeated word."
        else:
            self.games_history[email_address][word] = None
        event.set()
        return True, 'Word accepted'

    async def get_last_response(self, email_address):
        await lock.acquire()
        try:
            word = next(reversed(self.games_history[email_address]))
        finally:
            lock.release()
        return word

    async def get_event(self, email_address):
        await lock.acquire()
        try:
            event = self.events[email_address]
        finally:
            lock.release()
        return event
