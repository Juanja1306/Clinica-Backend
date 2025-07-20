import os
import httpx
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener valores del entorno
POSTGREST_URL = os.getenv("POSTGREST_URL")
POSTGREST_TOKEN = os.getenv("POSTGREST_TOKEN")

# Validar que las variables de entorno estén configuradas
if not POSTGREST_URL:
    raise ValueError("POSTGREST_URL no está configurada en las variables de entorno")
if not POSTGREST_TOKEN:
    raise ValueError("POSTGREST_TOKEN no está configurada en las variables de entorno")

# Cliente HTTP reutilizable - se inicializará al usarse
_client: Optional[httpx.AsyncClient] = None

async def get_client() -> httpx.AsyncClient:
    """Obtener o crear el cliente HTTP"""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=POSTGREST_URL,
            headers={
                "Authorization": f"Bearer {POSTGREST_TOKEN}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Prefer": "return=representation"  # Para obtener los datos insertados/actualizados
            },
            timeout=30.0  # Timeout de 30 segundos
        )
    return _client

async def close_client():
    """Cerrar el cliente HTTP"""
    global _client
    if _client:
        await _client.aclose()
        _client = None

# Función para hacer una solicitud GET a una tabla
async def get_all_from_table(table_name: str, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Obtener todos los registros de una tabla
    
    Args:
        table_name: Nombre de la tabla
        limit: Límite de registros (opcional)
        offset: Offset para paginación (opcional)
    """
    try:
        client = await get_client()
        params = {}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
            
        response = await client.get(f"/{table_name}", params=params)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error al obtener datos de {table_name}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener datos de {table_name}: {e}")
        raise

# Función para obtener un registro por ID
async def get_by_id(table_name: str, id_field: str, id_value: Any) -> Optional[Dict[str, Any]]:
    """
    Obtener un registro por ID
    
    Args:
        table_name: Nombre de la tabla
        id_field: Nombre del campo ID
        id_value: Valor del ID
    """
    try:
        client = await get_client()
        response = await client.get(f"/{table_name}?{id_field}=eq.{id_value}")
        response.raise_for_status()
        data = response.json()
        return data[0] if data else None
    except httpx.HTTPError as e:
        logger.error(f"Error al obtener registro de {table_name} con {id_field}={id_value}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener registro de {table_name}: {e}")
        raise

# Función para insertar un registro
async def insert_into_table(table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insertar un registro en una tabla
    
    Args:
        table_name: Nombre de la tabla
        data: Datos a insertar
    """
    try:
        client = await get_client()
        response = await client.post(f"/{table_name}", json=data)
        response.raise_for_status()
        return response.json()[0] if response.json() else {}
    except httpx.HTTPError as e:
        logger.error(f"Error al insertar en {table_name}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado al insertar en {table_name}: {e}")
        raise

# Función para actualizar un registro
async def update_record(table_name: str, id_field: str, id_value: Any, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actualizar un registro
    
    Args:
        table_name: Nombre de la tabla
        id_field: Nombre del campo ID
        id_value: Valor del ID
        data: Datos a actualizar
    """
    try:
        client = await get_client()
        response = await client.patch(f"/{table_name}?{id_field}=eq.{id_value}", json=data)
        response.raise_for_status()
        return response.json()[0] if response.json() else {}
    except httpx.HTTPError as e:
        logger.error(f"Error al actualizar {table_name} con {id_field}={id_value}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado al actualizar {table_name}: {e}")
        raise

# Función para eliminar un registro
async def delete_record(table_name: str, id_field: str, id_value: Any) -> bool:
    """
    Eliminar un registro
    
    Args:
        table_name: Nombre de la tabla
        id_field: Nombre del campo ID
        id_value: Valor del ID
    """
    try:
        client = await get_client()
        response = await client.delete(f"/{table_name}?{id_field}=eq.{id_value}")
        response.raise_for_status()
        return True
    except httpx.HTTPError as e:
        logger.error(f"Error al eliminar de {table_name} con {id_field}={id_value}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado al eliminar de {table_name}: {e}")
        raise

# Función para búsquedas con filtros
async def search_table(table_name: str, filters: Dict[str, Any], limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Buscar registros con filtros
    
    Args:
        table_name: Nombre de la tabla
        filters: Diccionario con filtros (campo: valor)
        limit: Límite de resultados
    """
    try:
        client = await get_client()
        query_params = []
        for field, value in filters.items():
            query_params.append(f"{field}=eq.{value}")
        
        query_string = "&".join(query_params)
        if limit:
            query_string += f"&limit={limit}"
            
        response = await client.get(f"/{table_name}?{query_string}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error al buscar en {table_name}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado al buscar en {table_name}: {e}")
        raise
