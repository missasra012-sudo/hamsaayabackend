from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError

router = APIRouter()

# -----------------------------
# JWT Configuration
# -----------------------------
SECRET_KEY = "SUPER_SECRET_KEY_1234567890_RANDOM"
ALGORITHM = "HS256"


# -----------------------------
# Password Hashing Setup
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# -----------------------------
# TEMP USER (YOU CAN REPLACE WITH TinyDB)
# -----------------------------
fake_users_db = {
    "hamsaaya": {
        "username": "hamsaaya",
        "hashed_password": pwd_context.hash("12345"[:72])  # bcrypt safe limit
    }
}


# -----------------------------
# Utility Functions
# -----------------------------
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# -----------------------------
# Login Route → Generate Token
# -----------------------------
@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Create JWT
    access_token = create_access_token(data={"sub": user["username"]})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# -----------------------------
# Protected Route
# -----------------------------
@router.get("/secure-data")
def read_secure_data(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return {"message": f"Hello {username}, access granted!"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")  