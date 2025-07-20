from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from database import get_all_from_table, get_by_id, insert_into_table, update_record, delete_record, search_table
from schemas.consulta import ConsultaCreate, ConsultaUpdate, ConsultaResponse, ConsultaWithPaciente
from utils import get_current_user, validate_cedula, format_date_for_db
from datetime import date
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router para consultas
router = APIRouter(
    prefix="/consultas",
    tags=["consultas médicas"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=ConsultaResponse, status_code=201)
async def crear_consulta(
    consulta_data: ConsultaCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Crear una nueva consulta médica (requiere autenticación de médico)
    """
    try:
        # Validar cédula del paciente
        if not validate_cedula(consulta_data.cedula_paciente):
            raise HTTPException(status_code=400, detail="Cédula inválida")
        
        # Verificar que el paciente existe
        paciente = await get_by_id("pacientes", "cedula", consulta_data.cedula_paciente)
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Si se especifica una cita, verificar que existe
        if consulta_data.cita_id:
            cita = await get_by_id("citas", "id", consulta_data.cita_id)
            if not cita:
                raise HTTPException(status_code=404, detail="Cita no encontrada")
            
            # Verificar que la cita corresponde al paciente
            if cita["cedula_paciente"] != consulta_data.cedula_paciente:
                raise HTTPException(
                    status_code=400, 
                    detail="La cita no corresponde al paciente especificado"
                )
        
        # Crear la consulta
        consulta_dict = {
            "fecha": format_date_for_db(consulta_data.fecha),
            "diagnostico": consulta_data.diagnostico,
            "tratamiento": consulta_data.tratamiento,
            "observaciones": consulta_data.observaciones,
            "cedula_paciente": consulta_data.cedula_paciente,
            "cita_id": consulta_data.cita_id
        }
        
        nueva_consulta = await insert_into_table("consultas", consulta_dict)
        logger.info(f"Consulta creada para paciente: {consulta_data.cedula_paciente}")
        
        return nueva_consulta
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear consulta: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{cedula_paciente}", response_model=List[ConsultaResponse])
async def obtener_historial_paciente(
    cedula_paciente: str,
    limit: int = Query(default=50, le=200, ge=1, description="Límite de resultados"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener historial clínico (consultas) de un paciente por cédula
    """
    try:
        # Validar cédula
        if not validate_cedula(cedula_paciente):
            raise HTTPException(status_code=400, detail="Cédula inválida")
        
        # Verificar que el paciente existe
        paciente = await get_by_id("pacientes", "cedula", cedula_paciente)
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Buscar consultas del paciente
        filtros = {"cedula_paciente": cedula_paciente}
        consultas = await search_table("consultas", filtros, limit=limit)
        
        return consultas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener historial del paciente {cedula_paciente}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/", response_model=List[ConsultaResponse])
async def obtener_consultas(
    fecha: Optional[date] = Query(None, description="Filtrar por fecha específica"),
    cedula_paciente: Optional[str] = Query(None, description="Filtrar por cédula del paciente"),
    limit: int = Query(default=100, le=200, ge=1, description="Límite de resultados"),
    offset: int = Query(default=0, ge=0, description="Número de registros a saltar"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener todas las consultas con filtros opcionales (requiere autenticación de médico)
    """
    try:
        filtros = {}
        
        if fecha:
            filtros["fecha"] = format_date_for_db(fecha)
        
        if cedula_paciente:
            if not validate_cedula(cedula_paciente):
                raise HTTPException(status_code=400, detail="Cédula inválida")
            filtros["cedula_paciente"] = cedula_paciente
        
        if filtros:
            consultas = await search_table("consultas", filtros, limit=limit)
        else:
            consultas = await get_all_from_table("consultas", limit=limit, offset=offset)
        
        return consultas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener consultas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/detalle/{consulta_id}", response_model=ConsultaResponse)
async def obtener_consulta(
    consulta_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener una consulta específica por ID
    """
    try:
        consulta = await get_by_id("consultas", "id", consulta_id)
        if not consulta:
            raise HTTPException(status_code=404, detail="Consulta no encontrada")
        return consulta
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener consulta {consulta_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/{consulta_id}", response_model=ConsultaResponse)
async def actualizar_consulta(
    consulta_id: int,
    consulta_data: ConsultaUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar una consulta existente (requiere autenticación de médico)
    """
    try:
        # Verificar que la consulta existe
        consulta_existente = await get_by_id("consultas", "id", consulta_id)
        if not consulta_existente:
            raise HTTPException(status_code=404, detail="Consulta no encontrada")
        
        # Preparar datos para actualización
        data_dict = {}
        if consulta_data.fecha:
            data_dict["fecha"] = format_date_for_db(consulta_data.fecha)
        if consulta_data.diagnostico is not None:
            data_dict["diagnostico"] = consulta_data.diagnostico
        if consulta_data.tratamiento is not None:
            data_dict["tratamiento"] = consulta_data.tratamiento
        if consulta_data.observaciones is not None:
            data_dict["observaciones"] = consulta_data.observaciones
        
        if not data_dict:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        consulta_actualizada = await update_record("consultas", "id", consulta_id, data_dict)
        logger.info(f"Consulta {consulta_id} actualizada")
        
        return consulta_actualizada
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar consulta {consulta_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.delete("/{consulta_id}")
async def eliminar_consulta(
    consulta_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Eliminar una consulta (requiere autenticación de médico)
    """
    try:
        # Verificar que la consulta existe
        consulta_existente = await get_by_id("consultas", "id", consulta_id)
        if not consulta_existente:
            raise HTTPException(status_code=404, detail="Consulta no encontrada")
        
        await delete_record("consultas", "id", consulta_id)
        logger.info(f"Consulta {consulta_id} eliminada")
        
        return {"mensaje": f"Consulta {consulta_id} eliminada correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar consulta {consulta_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor") 