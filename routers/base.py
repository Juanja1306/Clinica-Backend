from fastapi import APIRouter
from database import get_all_from_table
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router base
router = APIRouter(
    tags=["general"]
)

@router.get("/")
def read_root():
    """Endpoint raíz de la API"""
    return {"mensaje": "¡API de Clínica funcionando correctamente!"}

@router.get("/saludo/{nombre}")
def saludar(nombre: str):
    """Endpoint de saludo personalizado"""
    return {"saludo": f"Hola, {nombre}!"}

@router.get("/health")
async def health_check():
    """Verificar el estado de la aplicación y conexión a la base de datos"""
    try:
        # Intentar hacer una consulta simple para verificar la conexión
        await get_all_from_table("pacientes", limit=1)
        return {
            "status": "healthy",
            "database": "connected",
            "message": "Aplicación funcionando correctamente"
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "message": "Error de conexión a la base de datos"
        } 