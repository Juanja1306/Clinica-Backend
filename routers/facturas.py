from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from database import get_all_from_table, get_by_id, insert_into_table, update_record, delete_record, search_table
from schemas.factura import FacturaCreate, FacturaUpdate, FacturaResponse, FacturaWithPaciente
from utils import get_current_user, validate_cedula, format_date_for_db
from datetime import date
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router para facturas
router = APIRouter(
    prefix="/facturas",
    tags=["facturación"],
    responses={404: {"description": "No encontrado"}}
)

@router.post("/", response_model=FacturaResponse, status_code=201)
async def crear_factura(
    factura_data: FacturaCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Crear una nueva factura (requiere autenticación de médico)
    """
    try:
        # Validar cédula del paciente
        if not validate_cedula(factura_data.cedula_paciente):
            raise HTTPException(status_code=400, detail="Cédula inválida")
        
        # Verificar que el paciente existe
        paciente = await get_by_id("pacientes", "cedula", factura_data.cedula_paciente)
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Si se especifica una consulta, verificar que existe
        if factura_data.consulta_id:
            consulta = await get_by_id("consultas", "id", factura_data.consulta_id)
            if not consulta:
                raise HTTPException(status_code=404, detail="Consulta no encontrada")
            
            # Verificar que la consulta corresponde al paciente
            if consulta["cedula_paciente"] != factura_data.cedula_paciente:
                raise HTTPException(
                    status_code=400, 
                    detail="La consulta no corresponde al paciente especificado"
                )
        
        # Crear la factura
        factura_dict = {
            "fecha": format_date_for_db(factura_data.fecha),
            "valor": float(factura_data.valor),  # Convertir Decimal a float para JSON
            "descripcion": factura_data.descripcion,
            "cedula_paciente": factura_data.cedula_paciente,
            "consulta_id": factura_data.consulta_id
        }
        
        nueva_factura = await insert_into_table("facturas", factura_dict)
        logger.info(f"Factura creada para paciente: {factura_data.cedula_paciente}")
        
        return nueva_factura
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear factura: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/", response_model=List[FacturaResponse])
async def obtener_facturas(
    fecha: Optional[date] = Query(None, description="Filtrar por fecha específica"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta"),
    cedula_paciente: Optional[str] = Query(None, description="Filtrar por cédula del paciente"),
    limit: int = Query(default=100, le=200, ge=1, description="Límite de resultados"),
    offset: int = Query(default=0, ge=0, description="Número de registros a saltar"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener todas las facturas con filtros opcionales (requiere autenticación de médico)
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
            facturas = await search_table("facturas", filtros, limit=limit)
        else:
            facturas = await get_all_from_table("facturas", limit=limit, offset=offset)
        
        # Si hay filtro de rango de fechas, aplicar filtro adicional
        if fecha_desde and fecha_hasta and not fecha:
            from datetime import datetime
            facturas = [
                factura for factura in facturas
                if fecha_desde <= datetime.strptime(factura["fecha"], "%Y-%m-%d").date() <= fecha_hasta
            ]
        
        return facturas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener facturas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{cedula_paciente}", response_model=List[FacturaResponse])
async def obtener_facturas_paciente(
    cedula_paciente: str,
    limit: int = Query(default=50, le=200, ge=1, description="Límite de resultados"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener facturas históricas de un paciente por cédula
    """
    try:
        # Validar cédula
        if not validate_cedula(cedula_paciente):
            raise HTTPException(status_code=400, detail="Cédula inválida")
        
        # Verificar que el paciente existe
        paciente = await get_by_id("pacientes", "cedula", cedula_paciente)
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Buscar facturas del paciente
        filtros = {"cedula_paciente": cedula_paciente}
        facturas = await search_table("facturas", filtros, limit=limit)
        
        return facturas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener facturas del paciente {cedula_paciente}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/detalle/{factura_id}", response_model=FacturaResponse)
async def obtener_factura(
    factura_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener una factura específica por ID
    """
    try:
        factura = await get_by_id("facturas", "id", factura_id)
        if not factura:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        return factura
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener factura {factura_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/{factura_id}", response_model=FacturaResponse)
async def actualizar_factura(
    factura_id: int,
    factura_data: FacturaUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar una factura existente (requiere autenticación de médico)
    """
    try:
        # Verificar que la factura existe
        factura_existente = await get_by_id("facturas", "id", factura_id)
        if not factura_existente:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        
        # Preparar datos para actualización
        data_dict = {}
        if factura_data.fecha:
            data_dict["fecha"] = format_date_for_db(factura_data.fecha)
        if factura_data.valor is not None:
            data_dict["valor"] = float(factura_data.valor)
        if factura_data.descripcion is not None:
            data_dict["descripcion"] = factura_data.descripcion
        
        if not data_dict:
            raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")
        
        factura_actualizada = await update_record("facturas", "id", factura_id, data_dict)
        logger.info(f"Factura {factura_id} actualizada")
        
        return factura_actualizada
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar factura {factura_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.delete("/{factura_id}")
async def eliminar_factura(
    factura_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Eliminar una factura (requiere autenticación de médico)
    """
    try:
        # Verificar que la factura existe
        factura_existente = await get_by_id("facturas", "id", factura_id)
        if not factura_existente:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        
        await delete_record("facturas", "id", factura_id)
        logger.info(f"Factura {factura_id} eliminada")
        
        return {"mensaje": f"Factura {factura_id} eliminada correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar factura {factura_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/reportes/resumen")
async def obtener_resumen_facturas(
    fecha_desde: Optional[date] = Query(None, description="Fecha desde para el reporte"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta para el reporte"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener resumen de facturación por período (requiere autenticación de médico)
    """
    try:
        # Obtener todas las facturas si no hay filtros
        if fecha_desde and fecha_hasta:
            facturas = await get_all_from_table("facturas", limit=1000)
            # Filtrar por rango de fechas
            from datetime import datetime
            facturas = [
                factura for factura in facturas
                if fecha_desde <= datetime.strptime(factura["fecha"], "%Y-%m-%d").date() <= fecha_hasta
            ]
        else:
            facturas = await get_all_from_table("facturas", limit=1000)
        
        # Calcular resumen
        total_facturas = len(facturas)
        total_valor = sum(float(factura["valor"]) for factura in facturas)
        valor_promedio = total_valor / total_facturas if total_facturas > 0 else 0
        
        return {
            "periodo": {
                "fecha_desde": fecha_desde.isoformat() if fecha_desde else None,
                "fecha_hasta": fecha_hasta.isoformat() if fecha_hasta else None
            },
            "total_facturas": total_facturas,
            "total_valor": round(total_valor, 2),
            "valor_promedio": round(valor_promedio, 2),
            "facturas": facturas
        }
        
    except Exception as e:
        logger.error(f"Error al generar resumen de facturas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor") 