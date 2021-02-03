import asyncio
import os
import uuid

import uvicorn
from email_validator import validate_email, EmailNotValidError
from fastapi import FastAPI, status
from starlette.responses import JSONResponse

from word_chain_server.game_manager import GameManager
from word_chain_server.response_models import StartGameRequest, PlayWordRequest

app = FastAPI()
loop = asyncio.get_event_loop()

current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.realpath(os.path.join(current_dir, 'wordlist.json'))
game_manager = GameManager(input_file)


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
    msg = await game_manager.add_game(email_address, game_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"gameID": game_id, "msg": msg},
                        media_type="application/json")


@app.post("/play_word/{email_address}")
async def play_word(email_address, play_word_request: PlayWordRequest):
    result = await game_manager.check_user(email_address)
    if not result:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"Error": "No such user"},
                            media_type="application/json")
    result = await game_manager.check_timeout(email_address)
    if not result:
        await game_manager.reset(email_address)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"Error": "Timeout. Game finished."},
                            media_type="application/json")
    result = await game_manager.check_word(email_address, play_word_request.word)
    if not result:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"Error": "Invalid word"},
                            media_type="application/json")
    computer_response, scores = await game_manager.get_computer_response(email_address, play_word_request.word)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"computer_response": computer_response,
                                                                 "scores": {"user_score": scores[0],
                                                                            "computer_score": scores[1]}},
                        media_type="application/json")


@app.post("/end_game/{email_address}")
async def end_game(email_address):
    result = await game_manager.check_user(email_address)
    if not result:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"Error": "No such user"},
                            media_type="application/json")
    await game_manager.reset(email_address)
    return JSONResponse(status_code=status.HTTP_200_OK)


@app.get("/get_history/{email_address}")
async def get_history(email_address):
    result = await game_manager.check_user(email_address)
    if not result:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"Error": "No such user"},
                            media_type="application/json")
    history = await game_manager.get_history(email_address)
    return JSONResponse(status_code=status.HTTP_200_OK, content=history, media_type="application/json")


@app.get("/get_scores/{email_address}")
async def get_history(email_address):
    result = await game_manager.check_user(email_address)
    if not result:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"Error": "No such user"},
                            media_type="application/json")
    scores = await game_manager.get_scores(email_address)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"scores": {"user_score": scores[0],
                                                                            "computer_score": scores[1]}},
                        media_type="application/json")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
