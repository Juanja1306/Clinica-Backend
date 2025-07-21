# Auth.py
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional

from models import Usuario
from database import get_db, database
from schemas.auth import UserCreate, Token
from utils import get_current_user, verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60


@router.get("/check-db")
async def check_database():
    """Verificar la conexión a la base de datos y la estructura de la tabla"""
    try:
        # Verificar si la tabla usuarios existe
        result = await database.fetch_one(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'usuarios'
            )
            """
        )
        
        if result and result[0]:
            # Obtener estructura de la tabla
            columns = await database.fetch_all(
                """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'usuarios'
                ORDER BY ordinal_position
                """
            )
            return {
                "status": "success",
                "table_exists": True,
                "columns": [{"name": col[0], "type": col[1]} for col in columns]
            }
        else:
            return {
                "status": "error",
                "message": "La tabla 'usuarios' no existe",
                "table_exists": False
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error de conexión: {str(e)}"
        }


@router.post("/test-json")
async def test_json(request: Request):
    """Endpoint de prueba para verificar el parsing de JSON"""
    try:
        body = await request.json()
        return {"received": body, "type": str(type(body))}
    except Exception as e:
        return {"error": str(e), "body": await request.body()}


@router.post("/register", response_model=Token)
async def register(user: UserCreate, db = Depends(get_db)):
    try:
        # Verificar si el usuario ya existe
        existing_user = await database.fetch_one(
            "SELECT * FROM usuarios WHERE username = $1", 
            [user.username]
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Usuario ya existe")

        # Crear nuevo usuario
        hashed_pw = get_password_hash(user.password)
        query = """
        INSERT INTO usuarios (username, password_hash) 
        VALUES ($1, $2) 
        RETURNING id, username
        """
        nuevo_usuario = await database.fetch_one(query, [user.username, hashed_pw])

        access_token = create_access_token(data={"sub": nuevo_usuario["username"]})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    try:
        # Buscar usuario
        user = await database.fetch_one(
            "SELECT * FROM usuarios WHERE username = $1", 
            [form_data.username]
        )
        
        if not user or not verify_password(form_data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        access_token = create_access_token(data={"sub": user["username"]})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# Ruta protegida de prueba
@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "id": current_user["id"]}


