from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from database import get_all_from_table, get_by_id, insert_into_table, update_record, delete_record, search_table
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router para médicos
router = APIRouter(
    prefix="/medicos",
    tags=["médicos"],
    responses={404: {"description": "No encontrado"}}
)

@router.get("/")
async def obtener_medicos(
    limit: int = Query(default=100, le=200, ge=1, description="Límite de resultados"),
    offset: int = Query(default=0, ge=0, description="Número de registros a saltar")
):
    """Obtener todos los médicos de la base de datos"""
    try:
        medicos = await get_all_from_table("medicos", limit=limit, offset=offset)
        return {"medicos": medicos}
    except Exception as e:
        logger.error(f"Error al obtener médicos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{medico_id}")
async def obtener_medico(medico_id: int):
    """Obtener un médico específico por ID"""
    try:
        medico = await get_by_id("medicos", "id", medico_id)
        if not medico:
            raise HTTPException(status_code=404, detail="Médico no encontrado")
        return {"medico": medico}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener médico {medico_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/", status_code=201)
async def crear_medico(medico_data: Dict[str, Any]):
    """Crear un nuevo médico"""
    try:
        nuevo_medico = await insert_into_table("medicos", medico_data)
        return {"medico": nuevo_medico}
    except Exception as e:
        logger.error(f"Error al crear médico: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/especialidad/{especialidad}")
async def obtener_medicos_por_especialidad(
    especialidad: str,
    limit: int = Query(default=50, le=200, ge=1)
):
    """Obtener médicos por especialidad"""
    try:
        filtros = {"especialidad": especialidad}
        medicos = await search_table("medicos", filtros, limit=limit)
        return {"medicos": medicos, "especialidad": especialidad}
    except Exception as e:
        logger.error(f"Error al buscar médicos por especialidad {especialidad}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor") 