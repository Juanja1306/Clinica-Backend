from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import get_all_from_table, get_by_id, insert_into_table, update_record, delete_record, search_table
from schemas.paciente import PacienteCreate, PacienteUpdate, PacienteResponse, PacienteListResponse
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router para pacientes
router = APIRouter(
    prefix="/pacientes",
    tags=["pacientes"],
    responses={404: {"description": "No encontrado"}}
)

@router.get("/", response_model=List[PacienteResponse])
async def obtener_pacientes(
    limit: int = Query(default=100, le=200, ge=1, description="Límite de resultados"),
    offset: int = Query(default=0, ge=0, description="Número de registros a saltar")
):
    """Obtener todos los pacientes de la base de datos"""
    try:
        pacientes = await get_all_from_table("pacientes", limit=limit, offset=offset)
        return pacientes
    except Exception as e:
        logger.error(f"Error al obtener pacientes: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{paciente_id}", response_model=PacienteResponse)
async def obtener_paciente(paciente_id: int):
    """Obtener un paciente específico por ID"""
    try:
        paciente = await get_by_id("pacientes", "id", paciente_id)
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        return paciente
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener paciente {paciente_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/", response_model=PacienteResponse, status_code=201)
async def crear_paciente(paciente_data: PacienteCreate):
    """Crear un nuevo paciente"""
    try:
        # Convertir el modelo Pydantic a diccionario, excluyendo valores None
        data_dict = paciente_data.model_dump(exclude_unset=True)
        nuevo_paciente = await insert_into_table("pacientes", data_dict)
        return nuevo_paciente
    except Exception as e:
        logger.error(f"Error al crear paciente: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/{paciente_id}", response_model=PacienteResponse)
async def actualizar_paciente(paciente_id: int, paciente_data: PacienteUpdate):
    """Actualizar un paciente existente"""
    try:
        # Verificar que el paciente existe
        paciente_existente = await get_by_id("pacientes", "id", paciente_id)
        if not paciente_existente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Convertir a diccionario solo los campos que fueron proporcionados
        data_dict = paciente_data.model_dump(exclude_unset=True)
        if not data_dict:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        paciente_actualizado = await update_record("pacientes", "id", paciente_id, data_dict)
        return paciente_actualizado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar paciente {paciente_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.delete("/{paciente_id}")
async def eliminar_paciente(paciente_id: int):
    """Eliminar un paciente"""
    try:
        # Verificar que el paciente existe
        paciente_existente = await get_by_id("pacientes", "id", paciente_id)
        if not paciente_existente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        await delete_record("pacientes", "id", paciente_id)
        return {"mensaje": f"Paciente {paciente_id} eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar paciente {paciente_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/buscar/por-campo", response_model=List[PacienteResponse])
async def buscar_pacientes(
    nombre: Optional[str] = Query(None, description="Buscar por nombre"),
    apellido: Optional[str] = Query(None, description="Buscar por apellido"),
    email: Optional[str] = Query(None, description="Buscar por email"),
    telefono: Optional[str] = Query(None, description="Buscar por teléfono"),
    numero_documento: Optional[str] = Query(None, description="Buscar por número de documento"),
    limit: int = Query(default=50, le=200, ge=1, description="Límite de resultados")
):
    """Buscar pacientes por diferentes campos"""
    try:
        filtros = {}
        if nombre:
            filtros["nombre"] = nombre
        if apellido:
            filtros["apellido"] = apellido
        if email:
            filtros["email"] = email
        if telefono:
            filtros["telefono"] = telefono
        if numero_documento:
            filtros["numero_documento"] = numero_documento
        
        if not filtros:
            raise HTTPException(status_code=400, detail="Debe proporcionar al menos un filtro de búsqueda")
        
        pacientes = await search_table("pacientes", filtros, limit=limit)
        return pacientes
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al buscar pacientes: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor") 