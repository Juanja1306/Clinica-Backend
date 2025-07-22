from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas.facturas import Factura, FacturaCreate
from database import insert_into_table, get_all_from_table, get_facturas_by_paciente
from utils import get_current_user

router = APIRouter(
    prefix="/facturas",
    tags=["facturas"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Factura)
async def create_factura(payload: FacturaCreate, current_user: dict = Depends(get_current_user)):
    try:
        return await insert_into_table("factura", payload.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Factura])
async def get_facturas(current_user: dict = Depends(get_current_user)):
    return await get_all_from_table("factura")

@router.get("/{cedula}", response_model=List[Factura])
async def get_facturas_paciente(cedula: str, current_user: dict = Depends(get_current_user)):
    facturas = await get_facturas_by_paciente(cedula)
    if not facturas:
        raise HTTPException(status_code=404, detail="No se encontraron facturas para el paciente")
    return facturas
