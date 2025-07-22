from pydantic import BaseModel
from typing import Optional

class PacienteCreate(BaseModel):
    cedula: str
    nombres: str
    correo: Optional[str] = None
    telefono: Optional[str] = None

class Paciente(PacienteCreate):
    class Config:
        from_attributes = True
