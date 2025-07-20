from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class ConsultaBase(BaseModel):
    """Esquema base para consulta"""
    fecha: date = Field(..., description="Fecha de la consulta")
    diagnostico: Optional[str] = Field(None, description="Diagnóstico de la consulta")
    tratamiento: Optional[str] = Field(None, description="Tratamiento prescrito")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")
    cedula_paciente: str = Field(..., min_length=10, max_length=10, description="Cédula del paciente")

class ConsultaCreate(ConsultaBase):
    """Esquema para crear una consulta"""
    cita_id: Optional[int] = Field(None, description="ID de la cita asociada (opcional)")

class ConsultaUpdate(BaseModel):
    """Esquema para actualizar una consulta"""
    fecha: Optional[date] = None
    diagnostico: Optional[str] = None
    tratamiento: Optional[str] = None
    observaciones: Optional[str] = None

class ConsultaResponse(ConsultaBase):
    """Esquema de respuesta para consulta"""
    id: int
    cita_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class ConsultaWithPaciente(ConsultaResponse):
    """Esquema de consulta con información del paciente"""
    paciente_nombres: Optional[str] = None 