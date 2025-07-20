from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from database import get_all_from_table, get_by_id, insert_into_table, update_record, delete_record, search_table
from datetime import date, datetime
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router para citas
router = APIRouter(
    prefix="/citas",
    tags=["citas"],
    responses={404: {"description": "No encontrado"}}
)

@router.get("/")
async def obtener_citas(
    fecha_desde: Optional[date] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    limit: int = Query(default=100, le=200, ge=1, description="Límite de resultados"),
    offset: int = Query(default=0, ge=0, description="Número de registros a saltar")
):
    """Obtener todas las citas médicas"""
    try:
        citas = await get_all_from_table("citas", limit=limit, offset=offset)
        return {"citas": citas}
    except Exception as e:
        logger.error(f"Error al obtener citas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{cita_id}")
async def obtener_cita(cita_id: int):
    """Obtener una cita específica por ID"""
    try:
        cita = await get_by_id("citas", "id", cita_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        return {"cita": cita}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener cita {cita_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/", status_code=201)
async def crear_cita(cita_data: Dict[str, Any]):
    """Crear una nueva cita médica"""
    try:
        nueva_cita = await insert_into_table("citas", cita_data)
        return {"cita": nueva_cita}
    except Exception as e:
        logger.error(f"Error al crear cita: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/paciente/{paciente_id}")
async def obtener_citas_paciente(
    paciente_id: int,
    limit: int = Query(default=50, le=200, ge=1)
):
    """Obtener todas las citas de un paciente específico"""
    try:
        filtros = {"paciente_id": paciente_id}
        citas = await search_table("citas", filtros, limit=limit)
        return {"citas": citas, "paciente_id": paciente_id}
    except Exception as e:
        logger.error(f"Error al obtener citas del paciente {paciente_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/medico/{medico_id}")
async def obtener_citas_medico(
    medico_id: int,
    fecha: Optional[date] = Query(None, description="Fecha específica (YYYY-MM-DD)"),
    limit: int = Query(default=50, le=200, ge=1)
):
    """Obtener todas las citas de un médico específico"""
    try:
        filtros = {"medico_id": medico_id}
        if fecha:
            filtros["fecha"] = fecha.isoformat()
        
        citas = await search_table("citas", filtros, limit=limit)
        return {"citas": citas, "medico_id": medico_id}
    except Exception as e:
        logger.error(f"Error al obtener citas del médico {medico_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/{cita_id}")
async def actualizar_cita(cita_id: int, cita_data: Dict[str, Any]):
    """Actualizar una cita existente"""
    try:
        # Verificar que la cita existe
        cita_existente = await get_by_id("citas", "id", cita_id)
        if not cita_existente:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        cita_actualizada = await update_record("citas", "id", cita_id, cita_data)
        return {"cita": cita_actualizada}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar cita {cita_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor") 