# Auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

from models import Usuario
from database import get_db
from schemas.auth import UserCreate, Token
from utils import get_current_user
from utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60


@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(Usuario).filter_by(username=user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    hashed_pw = get_password_hash(user.password)
    nuevo_usuario = Usuario(username=user.username, password_hash=hashed_pw)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    access_token = create_access_token(data={"sub": nuevo_usuario.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter_by(username=form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Ruta protegida de prueba
@router.get("/me")
def get_current_user_info(current_user: Usuario = Depends(get_current_user)):
    return {"username": current_user.username, "id": current_user.id}


