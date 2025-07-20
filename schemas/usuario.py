from pydantic import BaseModel, Field
from typing import Optional

class UsuarioBase(BaseModel):
    """Esquema base para usuario"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")

class UsuarioCreate(UsuarioBase):
    """Esquema para crear usuario"""
    password: str = Field(..., min_length=4, description="Contraseña del usuario")

class UsuarioLogin(BaseModel):
    """Esquema para login"""
    username: str = Field(..., description="Nombre de usuario")
    password: str = Field(..., description="Contraseña")

class UsuarioResponse(UsuarioBase):
    """Esquema de respuesta para usuario"""
    id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Esquema para token de autenticación"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Esquema para datos del token"""
    username: Optional[str] = None 