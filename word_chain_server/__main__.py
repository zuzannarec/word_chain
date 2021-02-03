import asyncio
import os
import uuid

import uvicorn
from email_validator import validate_email, EmailNotValidError
from fastapi import FastAPI, status
from pydantic import BaseModel
from starlette.responses import JSONResponse

from word_chain_server.game_manager import GameManager

app = FastAPI()
loop = asyncio.get_event_loop()

current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.realpath(os.path.join(current_dir, 'wordlist.json'))
game_manager = GameManager(input_file)


class StartGameRequest(BaseModel):
    email_address: str


class PlayWordRequest(BaseModel):
    word: str


@app.post("/start_game")
async def start_game(start_game_request: StartGameRequest):
    game_id = str(uuid.uuid1().hex)
    email_address = start_game_request.email_address
    try:
        valid = validate_email(email_address)
        # Update with the normalized form.
        email_address = valid.email
    except EmailNotValidError:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"Error": "Invalid email"})
    await game_manager.add_game(email_address, game_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"gameID": game_id}, media_type="application/json")


@app.post("/play_word/{email_address}")
async def play_word(email_address, play_word_request: PlayWordRequest):
    result = await game_manager.check_timeout(email_address)
    if not result:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"Error": "Timeout. Game finished."},
                            media_type="application/json")
    result = await game_manager.check_word(email_address, play_word_request.word)
    if not result:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"Error": "Invalid word"},
                            media_type="application/json")
    computer_response = "WORD_COMPUTER"
    return JSONResponse(status_code=status.HTTP_200_OK, content={"computer_response": computer_response},
                        media_type="application/json")


@app.post("/end_game/{email_address}")
async def end_game(email_address):
    # TODO
    return JSONResponse(status_code=status.HTTP_200_OK)


@app.get("/end_game/{email_address}")
async def get_history(email_address):
    # TODO
    return JSONResponse(status_code=status.HTTP_200_OK)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
