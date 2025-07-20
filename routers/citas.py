from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from database import get_all_from_table, get_by_id, insert_into_table, update_record, delete_record, search_table
from schemas.cita import CitaCreate, CitaReservar, CitaUpdate, CitaResponse, CitaWithPaciente
from schemas.paciente import PacienteCreate
from utils import get_current_user, validate_cedula, format_date_for_db, format_time_for_db
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

@router.post("/reservar", response_model=CitaResponse, status_code=201)
async def reservar_cita(cita_data: CitaReservar):
    """
    Reservar una cita desde el frontend cliente (sin autenticación)
    Crea el paciente si no existe y luego crea la cita
    """
    try:
        # Validar cédula
        if not validate_cedula(cita_data.cedula):
            raise HTTPException(status_code=400, detail="Cédula inválida")
        
        # Verificar si el paciente ya existe
        paciente_existente = await get_by_id("pacientes", "cedula", cita_data.cedula)
        
        if not paciente_existente:
            # Crear paciente si no existe
            paciente_data = {
                "cedula": cita_data.cedula,
                "nombres": cita_data.nombres,
                "correo": cita_data.correo,
                "telefono": cita_data.telefono
            }
            await insert_into_table("pacientes", paciente_data)
            logger.info(f"Paciente creado con cédula: {cita_data.cedula}")
        
        # Verificar que no haya conflicto de horario
        fecha_str = format_date_for_db(cita_data.fecha)
        hora_str = format_time_for_db(cita_data.hora)
        
        # Buscar citas existentes en la misma fecha y hora
        filtros_cita = {"fecha": fecha_str, "hora": hora_str}
        citas_existentes = await search_table("citas", filtros_cita, limit=1)
        
        if citas_existentes:
            raise HTTPException(
                status_code=400, 
                detail="Ya existe una cita programada para esa fecha y hora"
            )
        
        # Crear la cita
        cita_dict = {
            "fecha": fecha_str,
            "hora": hora_str,
            "motivo": cita_data.motivo,
            "cedula_paciente": cita_data.cedula,
            "agendada_por_medico": False
        }
        
        nueva_cita = await insert_into_table("citas", cita_dict)
        logger.info(f"Cita reservada para paciente: {cita_data.cedula}")
        
        return nueva_cita
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al reservar cita: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/", response_model=CitaResponse, status_code=201)
async def crear_cita_medico(
    cita_data: CitaCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Crear una cita desde el panel del médico (requiere autenticación)
    """
    try:
        # Validar cédula
        if not validate_cedula(cita_data.cedula_paciente):
            raise HTTPException(status_code=400, detail="Cédula inválida")
        
        # Verificar que el paciente existe
        paciente = await get_by_id("pacientes", "cedula", cita_data.cedula_paciente)
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Verificar que no haya conflicto de horario
        fecha_str = format_date_for_db(cita_data.fecha)
        hora_str = format_time_for_db(cita_data.hora)
        
        filtros_cita = {"fecha": fecha_str, "hora": hora_str}
        citas_existentes = await search_table("citas", filtros_cita, limit=1)
        
        if citas_existentes:
            raise HTTPException(
                status_code=400, 
                detail="Ya existe una cita programada para esa fecha y hora"
            )
        
        # Crear la cita
        cita_dict = {
            "fecha": fecha_str,
            "hora": hora_str,
            "motivo": cita_data.motivo,
            "cedula_paciente": cita_data.cedula_paciente,
            "agendada_por_medico": True
        }
        
        nueva_cita = await insert_into_table("citas", cita_dict)
        logger.info(f"Cita creada por médico para paciente: {cita_data.cedula_paciente}")
        
        return nueva_cita
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear cita: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/", response_model=List[CitaResponse])
async def obtener_citas(
    fecha: Optional[date] = Query(None, description="Filtrar por fecha específica"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta"),
    limit: int = Query(default=100, le=200, ge=1, description="Límite de resultados"),
    offset: int = Query(default=0, ge=0, description="Número de registros a saltar"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener todas las citas (requiere autenticación de médico)
    Permite filtrar por fecha o rango de fechas
    """
    try:
        if fecha:
            # Filtrar por fecha específica
            fecha_str = format_date_for_db(fecha)
            filtros = {"fecha": fecha_str}
            citas = await search_table("citas", filtros, limit=limit)
        elif fecha_desde and fecha_hasta:
            # Para filtros de rango, necesitamos hacer múltiples consultas
            # PostgREST básico no soporta rangos directamente
            citas = await get_all_from_table("citas", limit=limit, offset=offset)
            # Filtrar en el lado de la aplicación
            citas = [
                cita for cita in citas 
                if fecha_desde <= datetime.strptime(cita["fecha"], "%Y-%m-%d").date() <= fecha_hasta
            ]
        else:
            # Obtener todas las citas
            citas = await get_all_from_table("citas", limit=limit, offset=offset)
        
        return citas
        
    except Exception as e:
        logger.error(f"Error al obtener citas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{cita_id}", response_model=CitaResponse)
async def obtener_cita(
    cita_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener una cita específica por ID (requiere autenticación de médico)
    """
    try:
        cita = await get_by_id("citas", "id", cita_id)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        return cita
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener cita {cita_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/{cita_id}", response_model=CitaResponse)
async def actualizar_cita(
    cita_id: int,
    cita_data: CitaUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar una cita existente (requiere autenticación de médico)
    """
    try:
        # Verificar que la cita existe
        cita_existente = await get_by_id("citas", "id", cita_id)
        if not cita_existente:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        # Preparar datos para actualización
        data_dict = {}
        if cita_data.fecha:
            data_dict["fecha"] = format_date_for_db(cita_data.fecha)
        if cita_data.hora:
            data_dict["hora"] = format_time_for_db(cita_data.hora)
        if cita_data.motivo is not None:
            data_dict["motivo"] = cita_data.motivo
        
        if not data_dict:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        # Verificar conflicto de horario si se actualiza fecha/hora
        if "fecha" in data_dict or "hora" in data_dict:
            fecha_check = data_dict.get("fecha", cita_existente["fecha"])
            hora_check = data_dict.get("hora", cita_existente["hora"])
            
            filtros_conflicto = {"fecha": fecha_check, "hora": hora_check}
            citas_conflicto = await search_table("citas", filtros_conflicto, limit=5)
            
            # Filtrar la cita actual
            citas_conflicto = [c for c in citas_conflicto if c["id"] != cita_id]
            
            if citas_conflicto:
                raise HTTPException(
                    status_code=400,
                    detail="Ya existe otra cita programada para esa fecha y hora"
                )
        
        cita_actualizada = await update_record("citas", "id", cita_id, data_dict)
        return cita_actualizada
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar cita {cita_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.delete("/{cita_id}")
async def cancelar_cita(
    cita_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancelar/eliminar una cita (requiere autenticación de médico)
    """
    try:
        # Verificar que la cita existe
        cita_existente = await get_by_id("citas", "id", cita_id)
        if not cita_existente:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        await delete_record("citas", "id", cita_id)
        return {"mensaje": f"Cita {cita_id} cancelada correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cancelar cita {cita_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor") 