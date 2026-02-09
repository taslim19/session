import os
import uuid
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from telethon import TelegramClient
from pyrogram import Client

app = FastAPI()

SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)


class SessionRequest(BaseModel):
    api_id: int
    api_hash: str
    bot_token: str
    session_name: str | None = None
    lib: str = "telethon"


@app.get("/")
def home():
    return {"status": "Session API running"}


@app.post("/generate")
async def generate_session(data: SessionRequest):
    name = data.session_name or str(uuid.uuid4())
    session_path = f"{SESSION_DIR}/{name}"

    if data.lib.lower() == "telethon":
        client = TelegramClient(
            session_path,
            data.api_id,
            data.api_hash
        )

        await client.start(bot_token=data.bot_token)
        await client.disconnect()

        return FileResponse(
            session_path + ".session",
            filename=name + ".session"
        )

    elif data.lib.lower() == "pyro":
        app_client = Client(
            name,
            api_id=data.api_id,
            api_hash=data.api_hash,
            bot_token=data.bot_token,
            workdir=SESSION_DIR,
        )

        await app_client.start()
        await app_client.stop()

        return FileResponse(
            f"{SESSION_DIR}/{name}.session",
            filename=name + ".session"
        )

    return {"error": "Unknown library"}
