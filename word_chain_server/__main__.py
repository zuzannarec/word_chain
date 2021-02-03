import asyncio
import uuid

import uvicorn
from email_validator import validate_email, EmailNotValidError
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from starlette.responses import JSONResponse

from word_chain_server.game_manager import GameManager

app = FastAPI()
loop = asyncio.get_event_loop()
game_manager = GameManager()


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
    except EmailNotValidError as e:
        return Response(status_code=status.WS_1003_UNSUPPORTED_DATA)
    await game_manager.add_game(email_address, game_id)
    asyncio.run_coroutine_threadsafe(game_manager.wait_for_users_response(email_address), loop)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"gameID": game_id}, media_type="application/json")


@app.post("/play_word/{email_address}")
async def play_word(email_address, play_word_request: PlayWordRequest):
    result, msg = await game_manager.set_event(email_address, play_word_request.word)
    print(msg)
    if result:
        computer_response = "WORD_COMPUTER"
        asyncio.run_coroutine_threadsafe(game_manager.wait_for_users_response(email_address), loop)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"computer_response": computer_response},
                            media_type="application/json")
    else:
        if 'Timeout' not in msg:
            asyncio.run_coroutine_threadsafe(game_manager.wait_for_users_response(email_address), loop)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"msg": msg},
                            media_type="application/json")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
