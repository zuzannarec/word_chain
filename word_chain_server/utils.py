import asyncio

ID_NAME = {"1": "Zuzanna",
           "2": "Tomasz"}


async def get_name_by_id(idx: str) -> str:
    await asyncio.sleep(5)
    return ID_NAME[idx]
