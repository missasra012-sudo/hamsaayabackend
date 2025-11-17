from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from tinydb import Query

from db import users, chats
from utils.emotion import detect_emotion, generate_reply

router = APIRouter()

class Message(BaseModel):
    username: str
    message: str

@router.post("/chat")
def chat(msg: Message):
    UserQuery = Query()
    user = users.search(UserQuery.username == msg.username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    language = user[0]["language"]

    # Emotion detect from *text*
    emotion = detect_emotion(msg.message)

    # Reply generator
    reply = generate_reply(emotion, language)

    chats.insert({
        "username": msg.username,
        "message": msg.message,
        "emotion": emotion,
        "reply": reply,
        "timestamp": datetime.now().isoformat()
    })

    return {
        "user_message": msg.message,
        "emotion": emotion,
        "reply": reply
    }

@router.get("/mood_history/{username}")
def mood_history(username: str):
    UserQuery = Query()
    user_chats = chats.search(UserQuery.username == username)

    if not user_chats:
        raise HTTPException(status_code=404, detail="No mood history found.")

    return {"history": user_chats}

@router.delete("/clear_chat/{username}")
def clear_chat(username: str):
    UserQuery = Query()
    chats.remove(UserQuery.username == username)
    return {"message": "Chat history cleared."}
