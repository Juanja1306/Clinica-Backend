# 🏥 Sistema de Gestión de Clínica - Backend API

Sistema backend completo para la gestión de una clínica médica desarrollado con **FastAPI** y **PostgreSQL**. Incluye funcionalidades separadas para pacientes (frontend público) y médicos (panel de administración).

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Variables de Entorno](#-variables-de-entorno)
- [Base de Datos](#-base-de-datos)
- [Documentación de la API](#-documentación-de-la-api)
- [Flujos de Trabajo](#-flujos-de-trabajo)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Seguridad](#-seguridad)
- [Solución de Problemas](#-solución-de-problemas)

## 🚀 Características

### Para Pacientes (Público)
- ✅ Registro automático de pacientes
- ✅ Reserva de citas sin autenticación
- ✅ Validación de cédula ecuatoriana

### Para Médicos (Autenticado)
- ✅ Autenticación JWT segura
- ✅ Gestión completa de pacientes
- ✅ Agenda de citas con control de horarios
- ✅ Historial clínico completo
- ✅ Sistema de facturación
- ✅ Reportes de facturación

### Técnicas
- ✅ API RESTful con FastAPI
- ✅ Documentación automática (Swagger/OpenAPI)
- ✅ Validación de datos con Pydantic
- ✅ Autenticación JWT
- ✅ Conexión a PostgreSQL via PostgREST
- ✅ Logging completo
- ✅ Manejo de errores robusto

## 🏗️ Arquitectura del Sistema

### Entidades Principales

```
Paciente (PK: cedula)
├── Cita (FK: cedula_paciente)
├── Consulta (FK: cedula_paciente, cita_id opcional)
└── Factura (FK: cedula_paciente, consulta_id opcional)

Usuario (solo médico)
```

### Estructura del Proyecto

```
Clinica-Backend/
├── main.py                 # Aplicación principal FastAPI
├── config.py              # Configuración y variables de entorno
├── database.py            # Cliente PostgREST y funciones de BD
├── utils.py               # Utilidades de autenticación y validación
├── requirements.txt       # Dependencias Python
├── routers/              # Endpoints organizados por módulo
│   ├── auth.py           # Autenticación del médico
│   ├── base.py           # Endpoints generales
│   ├── pacientes.py      # Gestión de pacientes
│   ├── citas.py          # Gestión de citas
│   ├── consultas.py      # Consultas médicas
│   └── facturas.py       # Sistema de facturación
└── schemas/              # Modelos Pydantic
    ├── paciente.py
    ├── cita.py
    ├── consulta.py
    ├── usuario.py
    └── factura.py
```

## 🛠️ Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- PostgreSQL con PostgREST configurado
- pip (gestor de paquetes Python)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd Clinica-Backend
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Crear archivo .env en la raíz del proyecto
cp .env.example .env
# Editar .env con tus credenciales
```

5. **Ejecutar la aplicación**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: `http://localhost:8000`

## 🔧 Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Configuración de la Base de Datos PostgreSQL
POSTGREST_URL=http://localhost:3000
POSTGREST_TOKEN=your_postgrest_token_here

# Configuración de Seguridad JWT
SECRET_KEY=your-super-secret-jwt-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración de la aplicación
LOG_LEVEL=INFO
GOOGLE_CLOUD_PROJECT=your_project_name

# Configuración del entorno
ENVIRONMENT=development
```

### Descripción de Variables

- `POSTGREST_URL`: URL de tu instancia PostgREST
- `POSTGREST_TOKEN`: Token de autenticación para PostgREST
- `SECRET_KEY`: Clave secreta para firmar tokens JWT (¡CAMBIAR EN PRODUCCIÓN!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Tiempo de expiración de tokens en minutos

## 🗄️ Base de Datos

### Esquema de Tablas

El sistema requiere las siguientes tablas en PostgreSQL:

```sql
-- Tabla de pacientes
CREATE TABLE pacientes (
    cedula CHAR(10) PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    correo VARCHAR(100),
    telefono VARCHAR(15)
);

-- Tabla de citas
CREATE TABLE citas (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    motivo TEXT,
    cedula_paciente CHAR(10) NOT NULL,
    agendada_por_medico BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (cedula_paciente) REFERENCES pacientes(cedula)
);

-- Tabla de consultas
CREATE TABLE consultas (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    diagnostico TEXT,
    tratamiento TEXT,
    observaciones TEXT,
    cedula_paciente CHAR(10) NOT NULL,
    cita_id INTEGER,
    FOREIGN KEY (cedula_paciente) REFERENCES pacientes(cedula),
    FOREIGN KEY (cita_id) REFERENCES citas(id)
);

-- Tabla de usuario (médico)
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- Tabla de facturas
CREATE TABLE facturas (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    valor NUMERIC(10, 2) NOT NULL,
    descripcion TEXT,
    cedula_paciente CHAR(10) NOT NULL,
    consulta_id INTEGER,
    FOREIGN KEY (cedula_paciente) REFERENCES pacientes(cedula),
    FOREIGN KEY (consulta_id) REFERENCES consultas(id)
);
```

### Configuración Inicial

1. **Crear usuario médico inicial**:
```sql
-- La contraseña debe ser hasheada con bcrypt
INSERT INTO usuario (username, password_hash) 
VALUES ('medico', '$2b$12$...'); -- Hash de tu contraseña
```

2. **Datos de prueba** (opcional):
```sql
-- Paciente de ejemplo
INSERT INTO pacientes (cedula, nombres, correo, telefono) 
VALUES ('1234567890', 'Juan Pérez', 'juan@email.com', '0987654321');
```

## 📚 Documentación de la API

### Documentación Interactiva

Una vez que la aplicación esté ejecutándose:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Endpoints Principales

#### 🔓 Endpoints Públicos (Sin Autenticación)

##### Crear Paciente
```http
POST /pacientes/
Content-Type: application/json

{
  "cedula": "1234567890",
  "nombres": "Juan Pérez",
  "correo": "juan@email.com",
  "telefono": "0987654321"
}
```

##### Reservar Cita (Cliente)
```http
POST /citas/reservar
Content-Type: application/json

{
  "cedula": "1234567890",
  "nombres": "Juan Pérez",
  "correo": "juan@email.com",
  "telefono": "0987654321",
  "fecha": "2024-01-15",
  "hora": "10:30:00",
  "motivo": "Consulta general"
}
```

#### 🔐 Endpoints Autenticados (Médico)

##### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "medico",
  "password": "tu_contraseña"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

##### Gestión de Pacientes
```http
GET /pacientes/                          # Listar pacientes
GET /pacientes/{cedula}                   # Obtener paciente por cédula
PUT /pacientes/{cedula}                   # Actualizar paciente
DELETE /pacientes/{cedula}                # Eliminar paciente
```

##### Gestión de Citas
```http
GET /citas/                              # Listar citas
POST /citas/                             # Crear cita (médico)
GET /citas/{id}                          # Obtener cita específica
PUT /citas/{id}                          # Actualizar cita
DELETE /citas/{id}                       # Cancelar cita
```

##### Consultas Médicas
```http
POST /consultas/                         # Crear consulta
GET /consultas/{cedula_paciente}         # Historial del paciente
GET /consultas/                          # Listar consultas
GET /consultas/detalle/{id}              # Obtener consulta específica
PUT /consultas/{id}                      # Actualizar consulta
DELETE /consultas/{id}                   # Eliminar consulta
```

##### Facturación
```http
POST /facturas/                          # Crear factura
GET /facturas/                           # Listar facturas
GET /facturas/{cedula_paciente}          # Facturas del paciente
GET /facturas/detalle/{id}               # Obtener factura específica
PUT /facturas/{id}                       # Actualizar factura
DELETE /facturas/{id}                    # Eliminar factura
GET /facturas/reportes/resumen           # Resumen de facturación
```

### Autenticación

Para endpoints protegidos, incluir el token en el header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## 🔄 Flujos de Trabajo

### Flujo Cliente (Frontend Público)

1. **Reservar Cita**:
   ```
   Cliente → POST /citas/reservar
   ├── Sistema verifica cédula
   ├── Crea paciente si no existe
   ├── Verifica disponibilidad de horario
   └── Crea cita con agendada_por_medico=false
   ```

### Flujo Médico (Panel de Administración)

1. **Login**:
   ```
   Médico → POST /auth/login → Recibe JWT token
   ```

2. **Consultar Agenda**:
   ```
   Médico → GET /citas/?fecha=2024-01-15 → Lista de citas del día
   ```

3. **Atender Paciente**:
   ```
   a) Médico → GET /pacientes/{cedula} → Datos del paciente
   b) Médico → GET /consultas/{cedula} → Historial médico
   c) Médico → POST /consultas/ → Registra nueva consulta
   d) Médico → POST /facturas/ → Genera factura
   ```

4. **Gestionar Citas**:
   ```
   Médico → POST /citas/ → Agendar nueva cita
   Médico → PUT /citas/{id} → Modificar cita existente
   Médico → DELETE /citas/{id} → Cancelar cita
   ```

## 💡 Ejemplos de Uso

### Ejemplo Completo: Flujo de Atención

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Login del médico
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "medico",
    "password": "mi_contraseña"
})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Ver citas del día
citas = requests.get(
    f"{BASE_URL}/citas/?fecha=2024-01-15", 
    headers=headers
).json()

# 3. Obtener datos del paciente
cedula_paciente = "1234567890"
paciente = requests.get(
    f"{BASE_URL}/pacientes/{cedula_paciente}", 
    headers=headers
).json()

# 4. Ver historial médico
historial = requests.get(
    f"{BASE_URL}/consultas/{cedula_paciente}", 
    headers=headers
).json()

# 5. Registrar nueva consulta
consulta = requests.post(f"{BASE_URL}/consultas/", 
    headers=headers,
    json={
        "fecha": "2024-01-15",
        "diagnostico": "Hipertensión leve",
        "tratamiento": "Enalapril 10mg cada 12h",
        "observaciones": "Control en 2 semanas",
        "cedula_paciente": cedula_paciente,
        "cita_id": 1
    }
).json()

# 6. Generar factura
factura = requests.post(f"{BASE_URL}/facturas/", 
    headers=headers,
    json={
        "fecha": "2024-01-15",
        "valor": 40.00,
        "descripcion": "Consulta médica general",
        "cedula_paciente": cedula_paciente,
        "consulta_id": consulta["id"]
    }
).json()

print(f"Consulta registrada ID: {consulta['id']}")
print(f"Factura generada ID: {factura['id']}")
```

## 🔒 Seguridad

### Características de Seguridad Implementadas

- **Autenticación JWT**: Tokens seguros con expiración
- **Validación de cédula**: Algoritmo de validación ecuatoriana
- **Hashing de contraseñas**: bcrypt para almacenamiento seguro
- **Validación de datos**: Pydantic para validación estricta
- **CORS configurado**: Control de acceso desde frontends
- **Logging de seguridad**: Registro de intentos de login

### Recomendaciones de Producción

1. **Cambiar SECRET_KEY**: Usar una clave robusta en producción
2. **HTTPS**: Implementar certificados SSL/TLS
3. **Variables de entorno**: No commitear credenciales al repositorio
4. **Rate limiting**: Implementar límites de peticiones
5. **Backup de BD**: Configurar respaldos automáticos

## 🐛 Solución de Problemas

### Problemas Comunes

#### Error de Conexión a Base de Datos
```
Error: POSTGREST_URL no está configurada
```
**Solución**: Verificar que el archivo `.env` existe y contiene las variables correctas.

#### Token JWT Inválido
```
401 Unauthorized: No se pudieron validar las credenciales
```
**Solución**: 
- Verificar que el token no haya expirado
- Asegurar que el header Authorization esté correcto
- Verificar que SECRET_KEY sea la misma

#### Cédula Inválida
```
400 Bad Request: Cédula inválida
```
**Solución**: La cédula debe tener exactamente 10 dígitos y pasar la validación ecuatoriana.

#### Conflicto de Horarios
```
400 Bad Request: Ya existe una cita programada para esa fecha y hora
```
**Solución**: Verificar disponibilidad antes de agendar o cambiar horario.

### Logs Útiles

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Buscar errores específicos
grep "ERROR" logs/app.log

# Ver intentos de login
grep "Login" logs/app.log
```

### Health Check

Verificar que la aplicación esté funcionando:

```http
GET /health

Response:
{
  "status": "healthy",
  "database": "connected",
  "message": "Aplicación funcionando correctamente"
}
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Equipo

Desarrollado para sistema de clínica médica con separación clara entre funcionalidades públicas y privadas.

---

**¿Necesitas ayuda?** Revisa la documentación interactiva en `/docs` o consulta los logs de la aplicación para más detalles sobre errores específicos. 