from pydantic import BaseModel, Field
from typing import Optional

class PacienteBase(BaseModel):
    cedula: str = Field(..., max_length=10)
    nombres: str = Field(..., max_length=100)
    correo: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, max_length=15)

class PacienteCreate(PacienteBase):
    pass

class Paciente(PacienteBase):
    class Config:
        orm_mode = True
