import os

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from sqlmodel import Session
import uvicorn

load_dotenv()

from db import init_db
from models import Interaction, Message
from routers import router as interactions_router
import g4f

g4f.version_check = False
g4f.logging = True

app = FastAPI()


@app.on_event('startup')
async def init_app():
    init_db()
    # seed_data()


app.include_router(interactions_router)


if __name__ == "__main__":
    uvicorn("app", host="127.0.0.1", port=8000)