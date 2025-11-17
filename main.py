from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from users import router as users_router
from chat import router as chat_router
from auth import router as auth_router

app = FastAPI(title="🌟 Hamsaaya Advanced Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all modules
app.include_router(users_router)
app.include_router(chat_router)
app.include_router(auth_router)

@app.get("/")
def home():
    return {"message": "Welcome to Hamsaaya Backend ❤️"}
