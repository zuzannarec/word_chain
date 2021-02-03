from fastapi import APIRouter, Response

from word_chain_server.utils import get_name_by_id

router = APIRouter()


@router.get("/hello/{idx}")
async def hello(idx):
    name = await get_name_by_id(idx)
    response = Response(status_code=200, content=name, media_type="application/json")
    response.headers["hello_header"] = "alone in the world"
    return response
