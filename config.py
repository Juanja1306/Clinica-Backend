import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuración de la aplicación"""
    
    # Base de datos
    POSTGREST_URL: str = os.getenv("POSTGREST_URL", "")
    POSTGREST_TOKEN: str = os.getenv("POSTGREST_TOKEN", "")
    
    # Aplicación
    APP_NAME: str = "Clínica Backend API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API backend para sistema de clínica con PostgreSQL"
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]  # En producción, especificar dominios exactos
    ALLOWED_METHODS: list = ["*"]
    ALLOWED_HEADERS: list = ["*"]
    
    # Paginación
    DEFAULT_PAGE_SIZE: int = 100
    MAX_PAGE_SIZE: int = 200
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # JWT (si usas autenticación propia)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    
    @property
    def database_configured(self) -> bool:
        """Verificar si la base de datos está configurada"""
        return bool(self.POSTGREST_URL and self.POSTGREST_TOKEN)

# Instancia global de configuración
settings = Settings() 