import uvicorn
from fastapi import FastAPI

from alohi_server import users

app = FastAPI()
app.include_router(users.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
