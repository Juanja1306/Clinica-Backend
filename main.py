from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import connect_db, disconnect_db
from routers import health, auth, pacientes, citas, consultas, facturas
from config import settings
import logging

# Configurar logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando aplicación...")
    if not settings.database_configured:
        logger.warning("⚠️  Base de datos no configurada. Revisa las variables de entorno.")
    else:
        logger.info("✅ Configuración de base de datos encontrada")
        try:
            await connect_db()
            logger.info("✅ Conexión a PostgreSQL establecida")
        except Exception as e:
            logger.error(f"❌ Error conectando a base de datos: {e}")
    yield
    # Shutdown
    logger.info("Cerrando conexiones...")
    await disconnect_db()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Incluir routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(pacientes.router)
app.include_router(citas.router)
app.include_router(consultas.router)
app.include_router(facturas.router)

# Evento de startup adicional para logging
@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} iniciado")
    logger.info(f"📚 Documentación disponible en: /docs")
    logger.info(f"🔄 ReDoc disponible en: /redoc")
    logger.info("🔐 Endpoints públicos: POST /citas/reservar, POST /pacientes/")
    logger.info("🩺 Endpoints médicos: /auth/login, /consultas/, /facturas/, /citas/, /pacientes/")
    logger.info(f"🗄️  Conectando a: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
