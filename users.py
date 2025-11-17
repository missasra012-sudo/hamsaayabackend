from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from tinydb import Query
from db import users

router = APIRouter()

# -----------------------------------
# User Model
# -----------------------------------
class User(BaseModel):
    username: str
    password: str
    language: str = "english"


# -----------------------------------
# Signup Route
# -----------------------------------
@router.post("/signup")
def signup(user: User):
    UserQuery = Query()

    # Check if user exists
    if users.search(UserQuery.username == user.username):
        raise HTTPException(status_code=400, detail="Username already exists.")

    # Insert new user
    users.insert(user.dict())

    return {"message": f"Welcome to Hamsaaya, {user.username}!"}


# -----------------------------------
# Login Route
# -----------------------------------
@router.post("/login")
def login(user: User):
    UserQuery = Query()

    found = users.search(
        (UserQuery.username == user.username) &
        (UserQuery.password == user.password)
    )

    if not found:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    return {
        "message": "Login successful!",
        "username": user.username,
        "language": found[0]["language"]
    }


# -----------------------------------
# Update Language Route
# -----------------------------------
@router.post("/set_language")
def set_language(user: User):
    UserQuery = Query()

    # Check if user exists
    if not users.search(UserQuery.username == user.username):
        raise HTTPException(status_code=404, detail="User not found.")

    # Update language only
    users.update({"language": user.language}, UserQuery.username == user.username)

    return {"message": f"Language updated to {user.language}"}
