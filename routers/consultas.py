from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas.consultas import Consulta, ConsultaCreate
from database import insert_into_table, get_consultas_by_paciente
from utils import get_current_user

router = APIRouter(
    prefix="/consultas",
    tags=["consultas"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Consulta)
async def create_consulta(payload: ConsultaCreate, current_user: dict = Depends(get_current_user)):
    try:
        return await insert_into_table("consulta", payload.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{cedula}", response_model=List[Consulta])
async def get_consultas(cedula: str, current_user: dict = Depends(get_current_user)):
    consultas = await get_consultas_by_paciente(cedula)
    if not consultas:
        raise HTTPException(status_code=404, detail="No se encontraron consultas para el paciente")
    return consultas
