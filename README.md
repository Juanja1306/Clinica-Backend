# Clínica Backend API

API backend para sistema de clínica desarrollada con FastAPI y PostgreSQL vía PostgREST.

## 🏗️ Arquitectura

- **FastAPI**: Framework web moderno y rápido
- **PostgreSQL**: Base de datos relacional en Google Cloud SQL
- **PostgREST**: API REST automática sobre PostgreSQL
- **Google Cloud**: Infraestructura en la nube

## 📁 Estructura del Proyecto

```
Clinica-Backend/
├── main.py                 # Aplicación principal
├── database.py             # Conexión y operaciones de base de datos
├── config.py               # Configuración centralizada
├── requirements.txt        # Dependencias de Python
├── routers/               # Endpoints organizados por módulos
│   ├── __init__.py
│   ├── base.py            # Endpoints generales
│   ├── pacientes.py       # Gestión de pacientes
│   ├── medicos.py         # Gestión de médicos
│   └── citas.py           # Gestión de citas médicas
├── schemas/               # Validación de datos con Pydantic
│   ├── __init__.py
│   └── paciente.py        # Esquemas para pacientes
└── utils.py               # Utilidades generales
```

## 🚀 Instalación y Configuración

### 1. Clonar y configurar entorno

```bash
# Clonar el repositorio
git clone <repository-url>
cd Clinica-Backend

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Configuración de PostgREST para Google Cloud SQL PostgreSQL
POSTGREST_URL=https://tu-postgrest-instance.run.app
POSTGREST_TOKEN=tu-jwt-token-aqui

# Configuración adicional (opcional)
LOG_LEVEL=INFO
SECRET_KEY=tu-clave-secreta-aqui
GOOGLE_CLOUD_PROJECT=tu-proyecto-gcp
```

### 3. Ejecutar la aplicación

```bash
# Desarrollo
uvicorn main:app --reload

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📚 Documentación de la API

Una vez que la aplicación esté ejecutándose:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🔗 Endpoints Principales

### Endpoints Generales
- `GET /` - Mensaje de bienvenida
- `GET /health` - Estado de la aplicación y conexión DB
- `GET /saludo/{nombre}` - Saludo personalizado

### Pacientes (`/pacientes`)
- `GET /pacientes/` - Obtener todos los pacientes
- `GET /pacientes/{id}` - Obtener paciente por ID
- `POST /pacientes/` - Crear nuevo paciente
- `PUT /pacientes/{id}` - Actualizar paciente
- `DELETE /pacientes/{id}` - Eliminar paciente
- `GET /pacientes/buscar/por-campo` - Buscar pacientes

### Médicos (`/medicos`)
- `GET /medicos/` - Obtener todos los médicos
- `GET /medicos/{id}` - Obtener médico por ID
- `POST /medicos/` - Crear nuevo médico
- `GET /medicos/especialidad/{especialidad}` - Médicos por especialidad

### Citas (`/citas`)
- `GET /citas/` - Obtener todas las citas
- `GET /citas/{id}` - Obtener cita por ID
- `POST /citas/` - Crear nueva cita
- `PUT /citas/{id}` - Actualizar cita
- `GET /citas/paciente/{id}` - Citas de un paciente
- `GET /citas/medico/{id}` - Citas de un médico

## 🛠️ Ejemplo de Uso

### Crear un paciente

```bash
curl -X POST "http://localhost:8000/pacientes/" \
     -H "Content-Type: application/json" \
     -d '{
       "nombre": "Juan",
       "apellido": "Pérez",
       "email": "juan.perez@email.com",
       "telefono": "1234567890",
       "fecha_nacimiento": "1990-01-15"
     }'
```

### Buscar pacientes

```bash
curl "http://localhost:8000/pacientes/buscar/por-campo?nombre=Juan&limit=10"
```

## 🔧 Configuración para Google Cloud

### 1. PostgreSQL en Cloud SQL
```bash
# Crear instancia PostgreSQL
gcloud sql instances create clinica-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1
```

### 2. PostgREST en Cloud Run
```bash
# Desplegar PostgREST
gcloud run deploy postgrest \
    --image postgrest/postgrest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

### 3. Variables de entorno
- Configurar `POSTGREST_URL` con la URL de Cloud Run
- Configurar `POSTGREST_TOKEN` con JWT válido

## 📝 Esquemas de Base de Datos

### Tabla Pacientes
```sql
CREATE TABLE pacientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    telefono VARCHAR(15),
    fecha_nacimiento DATE,
    direccion VARCHAR(200),
    sexo CHAR(1) CHECK (sexo IN ('M', 'F', 'O')),
    tipo_documento VARCHAR(50),
    numero_documento VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔍 Características

- ✅ **API RESTful completa** con operaciones CRUD
- ✅ **Validación de datos** con Pydantic
- ✅ **Documentación automática** con Swagger/ReDoc
- ✅ **Arquitectura modular** con routers
- ✅ **Manejo de errores** robusto
- ✅ **Logging configurable**
- ✅ **CORS configurado** para desarrollo/producción
- ✅ **Type hints** completos
- ✅ **Async/await** para alto rendimiento
- ✅ **Google Cloud Ready**

## 🚦 Health Check

```bash
curl http://localhost:8000/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "database": "connected",
  "message": "Aplicación funcionando correctamente"
}
```

## 🔐 Consideraciones de Seguridad

1. **Variables de entorno**: Nunca commits archivos `.env`
2. **JWT Tokens**: Usar tokens seguros para PostgREST
3. **CORS**: Configurar orígenes específicos en producción
4. **HTTPS**: Usar HTTPS en producción
5. **Validación**: Todos los inputs son validados con Pydantic

## 📞 Soporte

Para preguntas o problemas, revisar:
1. Los logs de la aplicación
2. El endpoint `/health` para verificar conectividad
3. La documentación en `/docs` 