from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class CitaReserve(BaseModel):
    cedula: str
    nombres: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    fecha: date
    hora: time
    motivo: Optional[str] = None

class Cita(BaseModel):
    id: int
    fecha: date
    hora: time
    motivo: Optional[str] = None
    cedula_paciente: str
    agendada_por_medico: bool

    class Config:
        from_attributes = True
