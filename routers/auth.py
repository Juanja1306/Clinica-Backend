from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from utils import authenticate_user, create_access_token
from schemas.usuario import UsuarioLogin, Token
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router para autenticación
router = APIRouter(
    prefix="/auth",
    tags=["autenticación"],
    responses={401: {"description": "No autorizado"}}
)

@router.post("/login", response_model=Token)
async def login_medico(user_credentials: UsuarioLogin):
    """
    Autenticar al médico y generar token de acceso
    
    Args:
        user_credentials: Credenciales del usuario (username y password)
        
    Returns:
        Token: Token de acceso JWT
        
    Raises:
        HTTPException: Si las credenciales son incorrectas
    """
    try:
        # Autenticar usuario
        user = await authenticate_user(user_credentials.username, user_credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear token de acceso
        access_token = create_access_token(data={"sub": user["username"]})
        
        logger.info(f"Login exitoso para usuario: {user['username']}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error durante login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/login-form", response_model=Token)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint alternativo para login usando OAuth2PasswordRequestForm
    Compatible con la documentación automática de FastAPI
    
    Args:
        form_data: Datos del formulario OAuth2
        
    Returns:
        Token: Token de acceso JWT
    """
    try:
        # Autenticar usuario
        user = await authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear token de acceso
        access_token = create_access_token(data={"sub": user["username"]})
        
        logger.info(f"Login exitoso para usuario: {user['username']}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error durante login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )