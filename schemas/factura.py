from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal

class FacturaBase(BaseModel):
    """Esquema base para factura"""
    fecha: date = Field(..., description="Fecha de la factura")
    valor: Decimal = Field(..., gt=0, decimal_places=2, description="Valor de la factura")
    descripcion: Optional[str] = Field(None, description="Descripción de los servicios facturados")
    cedula_paciente: str = Field(..., min_length=10, max_length=10, description="Cédula del paciente")

class FacturaCreate(FacturaBase):
    """Esquema para crear una factura"""
    consulta_id: Optional[int] = Field(None, description="ID de la consulta asociada (opcional)")

class FacturaUpdate(BaseModel):
    """Esquema para actualizar una factura"""
    fecha: Optional[date] = None
    valor: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    descripcion: Optional[str] = None

class FacturaResponse(FacturaBase):
    """Esquema de respuesta para factura"""
    id: int
    consulta_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class FacturaWithPaciente(FacturaResponse):
    """Esquema de factura con información del paciente"""
    paciente_nombres: Optional[str] = None 