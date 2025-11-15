from fastapi import APIRouter, HTTPException
from database import get_db
import schemas
from passlib.context import CryptContext
import jwt, os
from datetime import datetime, timedelta
from routers.utils import send_email, random_integer

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET", "secret123")
ALGORITHM = "HS256"

def hash_password(password: str):
    
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
    






@router.post("forget password")
def forget_password(payload: schemas.ForgetPassword):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (payload.email,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Email not found")    
        otp_code = random_integer()
        cur.execute("UPDATE users SET otp_code = ? WHERE email = ?", (otp_code, payload.email))
        send_email(payload.email, otp_code)
        

    return {"message": "email has been sent with otp."}        