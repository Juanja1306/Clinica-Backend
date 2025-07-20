from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime

class PacienteBase(BaseModel):
    """Esquema base para paciente"""
    cedula: str = Field(..., min_length=10, max_length=10, description="Cédula del paciente (10 dígitos)")
    nombres: str = Field(..., min_length=1, max_length=100, description="Nombres completos del paciente")
    correo: Optional[EmailStr] = Field(None, description="Correo electrónico del paciente")
    telefono: Optional[str] = Field(None, min_length=10, max_length=15, description="Teléfono del paciente")

class PacienteCreate(PacienteBase):
    """Esquema para crear un paciente"""
    pass

class PacienteUpdate(BaseModel):
    """Esquema para actualizar un paciente (todos los campos opcionales excepto cédula)"""
    nombres: Optional[str] = Field(None, min_length=1, max_length=100)
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, min_length=10, max_length=15)

class PacienteResponse(PacienteBase):
    """Esquema de respuesta para paciente"""
    
    class Config:
        from_attributes = True

class PacienteSearch(BaseModel):
    """Parámetros de búsqueda para pacientes"""
    search: Optional[str] = Field(None, description="Buscar por nombre o cédula")
    limit: int = Field(default=50, le=200)
    offset: int = Field(default=0, ge=0) 