# Clínica Backend API

## Descripción
API RESTful para gestionar pacientes, citas, consultas y facturas de una clínica.

## Características
- Autenticación con JWT
- Gestión de pacientes
- Reserva y gestión de citas médicas
- Registro y consulta de consultas
- Emisión y consulta de facturas
- Health check

## Tecnologías
- Python 3.12+
- FastAPI
- SQLAlchemy (con `databases`)
- PostgreSQL
- Pydantic
- Passlib y JOSE
- Uvicorn

## Requisitos Previos
- Python 3.12+
- PostgreSQL
- pip

## Instalación
```bash
git clone https://github.com/Juanja1306/Clinica-Backend
cd Clinica-Backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Variables de Entorno
Crear un archivo `.env` en la raíz con:
```
POSTGREST_URL=<host_db>
DB_PORT=<puerto_db>
DB_USER=<usuario_db>
DB_PASSWORD=<password_db>
DB_NAME=<nombre_db>
SECRET_KEY=<tu_clave_secreta>
```

## Ejecución
```bash
uvicorn main:app --reload
```
La API estará disponible en `http://localhost:8000`

## Documentación Interactiva
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Postman Collection: `Analisis.postman_collection.json`

## Endpoints

### Auth
| Método | Ruta            | Descripción                 |
|--------|-----------------|-----------------------------|
| POST   | /auth/register  | Registrar nuevo usuario     |
| POST   | /auth/login     | Obtener token JWT           |

### Pacientes
| Método | Ruta                 | Descripción                  |
|--------|----------------------|------------------------------|
| POST   | /pacientes/          | Crear nuevo paciente         |
| GET    | /pacientes/{cedula}  | Obtener datos de un paciente |
| GET    | /pacientes/          | Listar todos los pacientes   |

### Citas
| Método | Ruta                | Descripción                                      |
|--------|---------------------|--------------------------------------------------|
| POST   | /citas/reservar     | Reservar cita (público)                          |
| POST   | /citas/             | Agendar cita (requiere token, personal médico)   |
| GET    | /citas/             | Obtener todas las citas (requiere token)         |
| DELETE | /citas/{id}         | Eliminar una cita (requiere token)               |

### Consultas
| Método | Ruta                 | Descripción                                          |
|--------|----------------------|------------------------------------------------------|
| POST   | /consultas/          | Crear registro de consulta (requiere token)          |
| GET    | /consultas/{cedula}  | Obtener consultas de un paciente (requiere token)    |

### Facturas
| Método | Ruta                 | Descripción                                         |
|--------|----------------------|-----------------------------------------------------|
| POST   | /facturas/           | Crear factura (requiere token)                      |
| GET    | /facturas/           | Listar todas las facturas (requiere token)          |
| GET    | /facturas/{cedula}   | Obtener facturas de un paciente (requiere token)    |

### Health Check
| Método | Ruta          | Descripción      |
|--------|---------------|------------------|
| GET    | /health/      | Verificar estado |

## Licencia
MIT (o la que corresponda)

## Contribuciones
Contribuciones bienvenidas. Abrir issues o pull requests.

