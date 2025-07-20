from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from database import get_all_from_table, get_by_id, insert_into_table, update_record, delete_record, search_table
from schemas.paciente import PacienteCreate, PacienteUpdate, PacienteResponse, PacienteSearch
from utils import get_current_user, validate_cedula
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router para pacientes
router = APIRouter(
    prefix="/pacientes",
    tags=["pacientes"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=PacienteResponse, status_code=201)
async def crear_paciente(paciente_data: PacienteCreate):
    """
    Crear un nuevo paciente
    Puede ser usado desde el frontend cliente (sin autenticación) o desde el médico
    """
    try:
        # Validar cédula
        if not validate_cedula(paciente_data.cedula):
            raise HTTPException(status_code=400, detail="Cédula inválida")
        
        # Verificar si el paciente ya existe
        paciente_existente = await get_by_id("pacientes", "cedula", paciente_data.cedula)
        if paciente_existente:
            raise HTTPException(status_code=400, detail="Ya existe un paciente con esta cédula")
        
        # Convertir el modelo Pydantic a diccionario
        data_dict = paciente_data.model_dump(exclude_unset=True)
        nuevo_paciente = await insert_into_table("pacientes", data_dict)
        return nuevo_paciente
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear paciente: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{cedula}", response_model=PacienteResponse)
async def obtener_paciente(
    cedula: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener un paciente específico por cédula (requiere autenticación de médico)
    """
    try:
        # Validar cédula
        if not validate_cedula(cedula):
            raise HTTPException(status_code=400, detail="Cédula inválida")
        
        paciente = await get_by_id("pacientes", "cedula", cedula)
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        return paciente
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener paciente {cedula}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/", response_model=List[PacienteResponse])
async def obtener_pacientes(
    search: Optional[str] = Query(None, description="Buscar por nombre o cédula"),
    limit: int = Query(default=100, le=200, ge=1, description="Límite de resultados"),
    offset: int = Query(default=0, ge=0, description="Número de registros a saltar"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener todos los pacientes (requiere autenticación de médico)
    Incluye búsqueda opcional por nombre o cédula
    """
    try:
        if search:
            # Implementar búsqueda básica
            # PostgREST no soporta LIKE directamente, así que haremos búsquedas exactas
            # Primero intentar buscar por cédula exacta
            if search.isdigit() and len(search) == 10:
                paciente = await get_by_id("pacientes", "cedula", search)
                return [paciente] if paciente else []
            else:
                # Buscar por nombre (búsqueda exacta por limitaciones de PostgREST)
                filtros = {"nombres": search}
                pacientes = await search_table("pacientes", filtros, limit=limit)
                return pacientes
        else:
            pacientes = await get_all_from_table("pacientes", limit=limit, offset=offset)
            return pacientes
    except Exception as e:
        logger.error(f"Error al obtener pacientes: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/{cedula}", response_model=PacienteResponse)
async def actualizar_paciente(
    cedula: str,
    paciente_data: PacienteUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar un paciente existente (requiere autenticación de médico)
    """
    try:
        # Validar cédula
        if not validate_cedula(cedula):
            raise HTTPException(status_code=400, detail="Cédula inválida")
        
        # Verificar que el paciente existe
        paciente_existente = await get_by_id("pacientes", "cedula", cedula)
        if not paciente_existente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Convertir a diccionario solo los campos que fueron proporcionados
        data_dict = paciente_data.model_dump(exclude_unset=True)
        if not data_dict:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        paciente_actualizado = await update_record("pacientes", "cedula", cedula, data_dict)
        return paciente_actualizado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar paciente {cedula}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.delete("/{cedula}")
async def eliminar_paciente(
    cedula: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Eliminar un paciente (requiere autenticación de médico)
    """
    try:
        # Validar cédula
        if not validate_cedula(cedula):
            raise HTTPException(status_code=400, detail="Cédula inválida")
        
        # Verificar que el paciente existe
        paciente_existente = await get_by_id("pacientes", "cedula", cedula)
        if not paciente_existente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        await delete_record("pacientes", "cedula", cedula)
        return {"mensaje": f"Paciente con cédula {cedula} eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar paciente {cedula}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor") 