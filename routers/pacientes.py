from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas.paciente import Paciente, PacienteCreate
from database import get_by_id, get_all_from_table, insert_into_table

router = APIRouter(
    prefix="/pacientes",
    tags=["pacientes"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Paciente)
async def create_paciente(paciente: PacienteCreate):
    try:
        return await insert_into_table("paciente", paciente.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{cedula}", response_model=Paciente)
async def get_paciente(cedula: str):
    paciente = await get_by_id("paciente", "cedula", cedula)
    if not paciente:
        raise HTTPException(status_code=4.4, detail="Paciente no encontrado")
    return paciente

@router.get("/", response_model=List[Paciente])
async def get_pacientes():
    return await get_all_from_table("paciente")
