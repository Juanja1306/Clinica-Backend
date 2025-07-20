from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime

class PacienteBase(BaseModel):
    """Esquema base para paciente"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del paciente")
    apellido: str = Field(..., min_length=1, max_length=100, description="Apellido del paciente")
    email: Optional[EmailStr] = Field(None, description="Email del paciente")
    telefono: Optional[str] = Field(None, min_length=10, max_length=15, description="Teléfono del paciente")
    fecha_nacimiento: Optional[date] = Field(None, description="Fecha de nacimiento")
    direccion: Optional[str] = Field(None, max_length=200, description="Dirección del paciente")
    sexo: Optional[str] = Field(None, regex=r"^(M|F|Otro)$", description="Sexo del paciente")
    tipo_documento: Optional[str] = Field(None, description="Tipo de documento")
    numero_documento: Optional[str] = Field(None, description="Número de documento")

class PacienteCreate(PacienteBase):
    """Esquema para crear un paciente"""
    pass

class PacienteUpdate(BaseModel):
    """Esquema para actualizar un paciente (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, min_length=10, max_length=15)
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = Field(None, max_length=200)
    sexo: Optional[str] = Field(None, regex=r"^(M|F|Otro)$")
    tipo_documento: Optional[str] = None
    numero_documento: Optional[str] = None

class PacienteResponse(PacienteBase):
    """Esquema de respuesta para paciente"""
    id: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PacienteListResponse(BaseModel):
    """Esquema de respuesta para lista de pacientes"""
    pacientes: list[PacienteResponse]
    total: Optional[int] = None

class PacienteSearchParams(BaseModel):
    """Parámetros de búsqueda para pacientes"""
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    limit: int = Field(default=50, le=200)
    offset: int = Field(default=0, ge=0) 