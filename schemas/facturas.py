from pydantic import BaseModel
from typing import Optional
from datetime import date

class FacturaCreate(BaseModel):
    cedula_paciente: str
    valor: float
    descripcion: Optional[str] = None
    consulta_id: Optional[int] = None
    fecha: date

class Factura(FacturaCreate):
    id: int

    class Config:
        orm_mode = True
