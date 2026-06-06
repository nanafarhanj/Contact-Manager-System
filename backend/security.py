import os
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from database import get_session

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

security_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: Session = Depends(get_session),
):
    token = credentials.credentials

    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token Expired!")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Token Invalid!")


    from models import User

    user = session.get(User, payload["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="No User!")
    return user

def hash_password(password:str) -> str:
    hashed = bcrypt.hashpw(
        password.encode("utf-8"), #string to byte
        bcrypt.gensalt(),
    )
    return hashed.decode()

def verify_password(plain_password:str, hashed_password:str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_token(user_id:int) -> str:
    payload = {
        "user_id":user_id,
        "exp":datetime.utcnow() + timedelta(hours=24),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
