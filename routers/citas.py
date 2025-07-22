from fastapi import APIRouter, HTTPException, Depends
from schemas.citas import CitaReserve, Cita
from database import get_by_id, insert_into_table
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

@router.post("/agendar", response_model=Cita)
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
