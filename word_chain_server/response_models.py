from pydantic import BaseModel


class StartGameRequest(BaseModel):
    email_address: str


class PlayWordRequest(BaseModel):
    word: str
