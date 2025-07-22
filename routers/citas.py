from typing import List
from fastapi import APIRouter, HTTPException, Depends
from schemas.citas import CitaReserve, Cita
from database import delete_record, get_all_from_table, get_by_id, insert_into_table
from utils import get_current_user

router = APIRouter(
    prefix="/citas",
    tags=["citas"],
    responses={404: {"description": "Not found"}},
)

@router.post("/reservar", response_model=Cita)
async def reservar_cita(payload: CitaReserve):
    # Verificar si el paciente existe
    paciente = await get_by_id("paciente", "cedula", payload.cedula)
    if not paciente:
        # Crear paciente si no existe
        await insert_into_table("paciente", {
            "cedula": payload.cedula,
            "nombres": payload.nombres,
            "correo": payload.correo,
            "telefono": payload.telefono,
        })
    # Crear cita
    cita = await insert_into_table("cita", {
        "fecha": payload.fecha,
        "hora": payload.hora,
        "motivo": payload.motivo,
        "cedula_paciente": payload.cedula,
    })
    return cita

@router.post("/", response_model=Cita)
async def agendar_cita(
    payload: CitaReserve,
    current_user: dict = Depends(get_current_user),
):
    # Autorizado por médico: marcar agendada_por_medico=True
    paciente = await get_by_id("paciente", "cedula", payload.cedula)
    if not paciente:
        await insert_into_table("paciente", {
            "cedula": payload.cedula,
            "nombres": payload.nombres,
            "correo": payload.correo,
            "telefono": payload.telefono,
        })
    cita = await insert_into_table("cita", {
        "fecha": payload.fecha,
        "hora": payload.hora,
        "motivo": payload.motivo,
        "cedula_paciente": payload.cedula,
        "agendada_por_medico": True,
    })
    return cita

@router.get("/", response_model=List[Cita])
async def get_citas(
    current_user: dict = Depends(get_current_user),
):
    return await get_all_from_table("cita")

@router.delete("/{id}")
async def delete_cita(
    id: int,
    current_user: dict = Depends(get_current_user),
):
    success = await delete_record("cita", "id", id)
    return {"deleted": success}
