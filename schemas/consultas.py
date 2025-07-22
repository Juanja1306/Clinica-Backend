from pydantic import BaseModel
from typing import Optional
from datetime import date

class ConsultaCreate(BaseModel):
    cedula_paciente: str
    diagnostico: str
    tratamiento: str
    observaciones: Optional[str] = None
    cita_id: Optional[int] = None
    fecha: date

class Consulta(ConsultaCreate):
    id: int

    class Config:
        orm_mode = True
