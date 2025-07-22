import asyncpg
from databases import Database
from typing import Optional, Dict, Any, List
import logging
from config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base de datos usando databases + asyncpg
database = Database(settings.database_url)

async def connect_db():
    """Conectar a la base de datos"""
    try:
        await database.connect()
        logger.info("✅ Conexión a PostgreSQL establecida")
    except Exception as e:
        logger.error(f"❌ Error conectando a PostgreSQL: {e}")
        raise

async def disconnect_db():
    """Desconectar de la base de datos"""
    try:
        await database.disconnect()
        logger.info("✅ Conexión a PostgreSQL cerrada")
    except Exception as e:
        logger.error(f"❌ Error cerrando conexión: {e}")

# Alias para compatibilidad
async def close_client():
    """Cerrar conexión de base de datos"""
    await disconnect_db()

async def get_all_from_table(table_name: str, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Obtener todos los registros de una tabla
    """
    try:
        query = f"SELECT * FROM {table_name}"
        if limit is not None:
            query += f" LIMIT {limit}"
        if offset is not None:
            query += f" OFFSET {offset}"
        rows = await database.fetch_all(query)
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener datos de {table_name}: {e}")
        raise

async def get_by_id(table_name: str, id_field: str, id_value: Any) -> Optional[Dict[str, Any]]:
    """
    Obtener un registro por ID
    """
    try:
        # Usar parámetro nombrado para evitar error de bindparams con lista
        query = f"SELECT * FROM {table_name} WHERE {id_field} = :id_value"
        row = await database.fetch_one(query, {"id_value": id_value})
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error al obtener registro de {table_name} con {id_field}={id_value}: {e}")
        raise

async def insert_into_table(table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insertar un registro en una tabla
    """
    try:
        fields = list(data.keys())
        # Build named placeholders and map values
        param_map: Dict[str, Any] = {}
        placeholders: List[str] = []
        for i, field in enumerate(fields):
            key = f"param_{i+1}"
            placeholders.append(f":{key}")
            param_map[key] = data[field]
        query_str = (
            f"INSERT INTO {table_name} ({', '.join(fields)}) "
            f"VALUES ({', '.join(placeholders)}) "
            f"RETURNING *"
        )
        row = await database.fetch_one(query_str, param_map)
        return dict(row)
    except Exception as e:
        logger.error(f"Error al insertar en {table_name}: {e}")
        raise

async def update_record(table_name: str, id_field: str, id_value: Any, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actualizar un registro
    """
    try:
        fields = list(data.keys())
        set_clause = [f"{field} = ${i+1}" for i, field in enumerate(fields)]
        values = list(data.values())
        values.append(id_value)  # Agregar el ID al final
        
        query = f"""
        UPDATE {table_name} 
        SET {', '.join(set_clause)}
        WHERE {id_field} = ${len(values)}
        RETURNING *
        """
        
        row = await database.fetch_one(query, values)
        return dict(row) if row else {}
    except Exception as e:
        logger.error(f"Error al actualizar {table_name} con {id_field}={id_value}: {e}")
        raise

async def delete_record(table_name: str, id_field: str, id_value: Any) -> bool:
    """
    Eliminar un registro
    """
    try:
        # Usar parámetro nombrado para evitar error de bindparams con lista
        query = f"DELETE FROM {table_name} WHERE {id_field} = :id_value"
        await database.execute(query, {"id_value": id_value})
        return True
    except Exception as e:
        logger.error(f"Error al eliminar de {table_name} con {id_field}={id_value}: {e}")
        raise

async def search_table(table_name: str, filters: Dict[str, Any], limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Buscar registros con filtros
    """
    try:
        conditions = []
        values = []
        
        for i, (field, value) in enumerate(filters.items()):
            conditions.append(f"{field} = ${i+1}")
            values.append(value)
        
        query = f"SELECT * FROM {table_name}"
        if conditions:
            query += f" WHERE {' AND '.join(conditions)}"
        
        if limit:
            query += f" LIMIT ${len(values) + 1}"
            values.append(limit)
        
        rows = await database.fetch_all(query, values)
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al buscar en {table_name}: {e}")
        raise

async def execute_query(query: str, values: Optional[List] = None) -> List[Dict[str, Any]]:
    """
    Ejecutar consulta personalizada
    """
    try:
        if values is None:
            values = []
        rows = await database.fetch_all(query, values)
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error ejecutando consulta: {e}")
        raise

async def execute_query_one(query: str, values: Optional[List] = None) -> Optional[Dict[str, Any]]:
    """
    Ejecutar consulta que retorna un solo registro
    """
    try:
        if values is None:
            values = []
        row = await database.fetch_one(query, values)
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error ejecutando consulta: {e}")
        raise

# Dependency para FastAPI
async def get_db():
    """
    Dependency para obtener la instancia de la base de datos
    """
    return database


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Obtener un usuario por email
    """
    try:
        query = "SELECT * FROM usuario WHERE email = :email"
        row = await database.fetch_one(query, {"email": email})
        return dict(row) if row else None
    except Exception as e:  
        logger.error(f"Error al obtener usuario por email: {e}")
        raise

async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Obtener un usuario por username
    """
    try:
        query = "SELECT * FROM usuario WHERE username = :username"
        row = await database.fetch_one(query, {"username": username})
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error al obtener usuario por username: {e}")
        raise

async def get_consultas_by_paciente(cedula_paciente: str) -> List[Dict[str, Any]]:
    """
    Obtener todas las consultas de un paciente
    """
    try:
        query = "SELECT * FROM consulta WHERE cedula_paciente = :cedula_paciente"
        rows = await database.fetch_all(query, {"cedula_paciente": cedula_paciente})
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener consultas por paciente: {e}")
        raise

async def get_facturas_by_paciente(cedula_paciente: str) -> List[Dict[str, Any]]:
    """
    Obtener todas las facturas de un paciente
    """
    try:
        query = "SELECT * FROM factura WHERE cedula_paciente = :cedula_paciente"
        rows = await database.fetch_all(query, {"cedula_paciente": cedula_paciente})
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener facturas por paciente: {e}")
        raise
