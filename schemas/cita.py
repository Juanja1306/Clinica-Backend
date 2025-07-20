from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime

class CitaBase(BaseModel):
    """Esquema base para cita"""
    fecha: date = Field(..., description="Fecha de la cita")
    hora: time = Field(..., description="Hora de la cita")
    motivo: Optional[str] = Field(None, description="Motivo de la cita")
    cedula_paciente: str = Field(..., min_length=10, max_length=10, description="Cédula del paciente")

class CitaCreate(CitaBase):
    """Esquema para crear una cita (usado por el médico)"""
    pass

class CitaReservar(BaseModel):
    """Esquema para reservar una cita desde el cliente"""
    # Datos del paciente (se creará si no existe)
    cedula: str = Field(..., min_length=10, max_length=10, description="Cédula del paciente")
    nombres: str = Field(..., min_length=1, max_length=100, description="Nombres completos del paciente")
    correo: Optional[str] = Field(None, description="Correo electrónico del paciente")
    telefono: Optional[str] = Field(None, min_length=10, max_length=15, description="Teléfono del paciente")
    
    # Datos de la cita
    fecha: date = Field(..., description="Fecha de la cita")
    hora: time = Field(..., description="Hora de la cita")
    motivo: Optional[str] = Field(None, description="Motivo de la cita")

class CitaUpdate(BaseModel):
    """Esquema para actualizar una cita"""
    fecha: Optional[date] = None
    hora: Optional[time] = None
    motivo: Optional[str] = None

class CitaResponse(CitaBase):
    """Esquema de respuesta para cita"""
    id: int
    agendada_por_medico: bool = False
    
    class Config:
        from_attributes = True

class CitaWithPaciente(CitaResponse):
    """Esquema de cita con información del paciente"""
    paciente_nombres: Optional[str] = None
    paciente_telefono: Optional[str] = None 