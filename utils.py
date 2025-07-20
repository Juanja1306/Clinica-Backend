from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings
from database import get_by_id
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Configuración de encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de seguridad Bearer
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar una contraseña plana contra su hash
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Contraseña hasheada
        
    Returns:
        bool: True si la contraseña es correcta
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generar hash de una contraseña
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Contraseña hasheada
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear token de acceso JWT
    
    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración personalizado
        
    Returns:
        str: Token JWT
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Autenticar usuario con username y contraseña
    
    Args:
        username: Nombre de usuario
        password: Contraseña en texto plano
        
    Returns:
        dict o None: Datos del usuario si la autenticación es exitosa
    """
    try:
        # Buscar usuario por username
        user = await get_by_id("usuario", "username", username)
        if not user:
            return None
        
        # Verificar contraseña
        if not verify_password(password, user["password_hash"]):
            return None
            
        return user
    except Exception as e:
        logger.error(f"Error durante autenticación: {e}")
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Obtener el usuario actual desde el token JWT
    
    Args:
        credentials: Credenciales del header Authorization
        
    Returns:
        dict: Datos del usuario actual
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar token JWT
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Buscar usuario en la base de datos
    user = await get_by_id("usuario", "username", username)
    if user is None:
        raise credentials_exception
    
    return user

def validate_cedula(cedula: str) -> bool:
    """
    Validar formato de cédula ecuatoriana
    
    Args:
        cedula: Cédula a validar
        
    Returns:
        bool: True si la cédula es válida
    """
    # Verificar que tenga exactamente 10 dígitos
    if len(cedula) != 10 or not cedula.isdigit():
        return False
    
    # Algoritmo de validación de cédula ecuatoriana
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    
    for i in range(9):
        resultado = int(cedula[i]) * coeficientes[i]
        if resultado >= 10:
            resultado = resultado // 10 + resultado % 10
        suma += resultado
    
    digito_verificador = (10 - (suma % 10)) % 10
    return digito_verificador == int(cedula[9])

def format_time_for_db(time_obj) -> str:
    """
    Formatear tiempo para la base de datos
    
    Args:
        time_obj: Objeto time de Python
        
    Returns:
        str: Tiempo formateado para PostgREST
    """
    return time_obj.strftime("%H:%M:%S")

def format_date_for_db(date_obj) -> str:
    """
    Formatear fecha para la base de datos
    
    Args:
        date_obj: Objeto date de Python
        
    Returns:
        str: Fecha formateada para PostgREST
    """
    return date_obj.strftime("%Y-%m-%d")
