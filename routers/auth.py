# routers/auth.py
from fastapi import APIRouter, HTTPException
from database import get_db
import schemas
from passlib.context import CryptContext
import jwt, os
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET", "secret123")
ALGORITHM = "HS256"

def hash_password(password: str):
    # bcrypt supports only 72 bytes, truncate longer passwords safely
    return pwd_context.hash(password[:72])

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password[:72], hashed)


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
def register_user(payload: schemas.RegisterIn):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (payload.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_pw = hash_password(payload.password)
        cur.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
            (payload.email, hashed_pw, payload.role)
        )
        return {"message": "User registered successfully"}

@router.post("/login", response_model=schemas.TokenOut)
def login_user(payload: schemas.LoginIn):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (payload.email,))
        user = cur.fetchone()
        if not user or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_token({"sub": user["email"], "role": user["role"]})
        return {"access_token": token, "token_type": "bearer"}
