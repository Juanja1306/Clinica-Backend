import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuración de la aplicación"""
    
    # Base de datos PostgreSQL
    DB_HOST: str = os.getenv("POSTGREST_URL")
    DB_PORT: int = int(os.getenv("DB_PORT"))
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")
    
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
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    
    @property
    def database_url(self) -> str:
        """URL de conexión a PostgreSQL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def database_configured(self) -> bool:
        """Verificar si la base de datos está configurada"""
        return bool(self.DB_HOST and self.DB_USER and self.DB_PASSWORD and self.DB_NAME)

# Instancia global de configuración
settings = Settings() 