# Auth.py
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional

from database import get_db, database, insert_into_table
from schemas.auth import UserCreate, User
from utils import get_current_user, verify_password, get_password_hash, create_access_token, get_user_by_username

router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/register", response_model=User)
async def register(payload: UserCreate):
    try:
        payload.password_hash = get_password_hash(payload.password_hash)
        return await insert_into_table("usuario", payload.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=User)
async def login(payload: OAuth2PasswordRequestForm = Depends()):
    user = await get_user_by_username(payload.username)
    if not user or not verify_password(payload.password_hash, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user
