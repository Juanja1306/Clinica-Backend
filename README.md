# 🏥 Sistema de Gestión de Clínica - Backend API

Sistema backend completo para la gestión de una clínica médica desarrollado con **FastAPI** y **PostgreSQL directo**. Incluye funcionalidades separadas para pacientes (frontend público) y médicos (panel de administración).

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
- ✅ Autenticación JWT con bcrypt
- ✅ Conexión directa a PostgreSQL con asyncpg
- ✅ Pool de conexiones para alto rendimiento
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
├── database.py            # Conexión directa PostgreSQL con asyncpg
├── utils.py               # Utilidades de autenticación y validación
├── requirements.txt       # Dependencias Python
├── .env                   # Variables de entorno (crear localmente)
├── routers/              # Endpoints organizados por módulo
│   ├── auth.py           # Autenticación del médico
│   ├── base.py           # Endpoints generales
│   ├── pacientes.py      # Gestión de pacientes
│   ├── citas.py          # Gestión de citas
│   ├── consultas.py      # Consultas médicas
│   └── facturas.py       # Sistema de facturación
├── schemas/              # Modelos Pydantic
│   ├── paciente.py       # Esquemas de paciente
│   ├── cita.py           # Esquemas de cita
│   ├── consulta.py       # Esquemas de consulta
│   ├── usuario.py        # Esquemas de usuario
│   └── factura.py        # Esquemas de factura
└── sql/                  # Scripts SQL (si los hay)
```

## 🛠️ Instalación y Configuración

### Prerrequisitos

- Python 3.8+ (probado en Python 3.13)
- PostgreSQL 12+ funcionando
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
# Copiar y adaptar las variables de abajo
```

5. **Ejecutar la aplicación**
```bash
uvicorn main:app --reload
```

La API estará disponible en: `http://localhost:8000`

## 🔧 Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Configuración de la Base de Datos PostgreSQL
POSTGREST_URL=34.75.123.136
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=clinica

# Configuración de Seguridad JWT
SECRET_KEY=tu-clave-secreta-jwt-para-produccion-cambiar

# Configuración de la aplicación
LOG_LEVEL=INFO
```

### Descripción de Variables

- `POSTGREST_URL`: **IP o host de PostgreSQL** (no es PostgREST, es la IP directa)
- `DB_PORT`: Puerto de PostgreSQL (por defecto 5432)
- `DB_USER`: Usuario de PostgreSQL
- `DB_PASSWORD`: Contraseña de PostgreSQL
- `DB_NAME`: Nombre de la base de datos
- `SECRET_KEY`: Clave secreta para firmar tokens JWT (¡CAMBIAR EN PRODUCCIÓN!)
- `LOG_LEVEL`: Nivel de logging (DEBUG, INFO, WARNING, ERROR)

## 🗄️ Base de Datos

### Conexión PostgreSQL

El sistema se conecta **directamente** a PostgreSQL usando **asyncpg** con pool de conexiones para alto rendimiento.

### Esquema de Tablas

Ejecutar estos scripts en tu PostgreSQL:

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
-- Ejemplo con contraseña "medico123" hasheada
INSERT INTO usuario (username, password_hash) 
VALUES ('medico', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4ePcv9o1vS');
```

2. **Datos de prueba** (opcional):
```sql
-- Paciente de ejemplo
INSERT INTO pacientes (cedula, nombres, correo, telefono) 
VALUES ('1234567890', 'Juan Pérez', 'juan@email.com', '0987654321');

-- Cita de ejemplo
INSERT INTO citas (fecha, hora, motivo, cedula_paciente, agendada_por_medico)
VALUES ('2024-01-15', '10:30:00', 'Consulta general', '1234567890', false);
```

## 📚 Documentación de la API

### Documentación Interactiva

Una vez que la aplicación esté ejecutándose:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

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
  "password": "medico123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

##### Gestión de Pacientes
```http
GET /pacientes/                          # Listar pacientes (requiere auth)
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
GET /consultas/                          # Listar todas las consultas
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
   ├── Sistema valida cédula ecuatoriana
   ├── Crea paciente si no existe
   ├── Verifica disponibilidad de horario
   └── Crea cita con agendada_por_medico=false
   ```

### Flujo Médico (Panel de Administración)

1. **Login**:
   ```
   Médico → POST /auth/login → Recibe JWT token (30 min)
   ```

2. **Consultar Agenda**:
   ```
   Médico → GET /citas/?fecha=2024-01-15 → Lista de citas del día
   ```

3. **Atender Paciente**:
   ```
   a) Médico → GET /pacientes/{cedula} → Datos del paciente
   b) Médico → GET /consultas/{cedula} → Historial médico completo
   c) Médico → POST /consultas/ → Registra nueva consulta
   d) Médico → POST /facturas/ → Genera factura asociada
   ```

4. **Gestionar Citas**:
   ```
   Médico → POST /citas/ → Agendar nueva cita para paciente existente
   Médico → PUT /citas/{id} → Modificar cita existente
   Médico → DELETE /citas/{id} → Cancelar cita
   ```

## 💡 Ejemplos de Uso

### Ejemplo Completo: Flujo de Atención

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Verificar que la API esté funcionando
health = requests.get(f"{BASE_URL}/health").json()
print(f"API Status: {health['status']}")

# 2. Login del médico
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "medico",
    "password": "medico123"
})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 3. Ver citas del día
citas = requests.get(
    f"{BASE_URL}/citas/?fecha=2024-01-15", 
    headers=headers
).json()
print(f"Citas del día: {len(citas)}")

# 4. Obtener datos del paciente
cedula_paciente = "1234567890"
paciente = requests.get(
    f"{BASE_URL}/pacientes/{cedula_paciente}", 
    headers=headers
).json()
print(f"Paciente: {paciente['nombres']}")

# 5. Ver historial médico
historial = requests.get(
    f"{BASE_URL}/consultas/{cedula_paciente}", 
    headers=headers
).json()
print(f"Consultas previas: {len(historial)}")

# 6. Registrar nueva consulta
consulta = requests.post(f"{BASE_URL}/consultas/", 
    headers=headers,
    json={
        "fecha": "2024-01-15",
        "diagnostico": "Hipertensión leve",
        "tratamiento": "Enalapril 10mg cada 12h",
        "observaciones": "Control en 2 semanas",
        "cedula_paciente": cedula_paciente
    }
).json()

# 7. Generar factura
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

print(f"✅ Consulta registrada ID: {consulta['id']}")
print(f"✅ Factura generada ID: {factura['id']}, Valor: ${factura['valor']}")
```

### Ejemplo: Reserva de Cita desde Cliente

```python
import requests

BASE_URL = "http://localhost:8000"

# Cliente reserva cita (sin autenticación)
nueva_cita = requests.post(f"{BASE_URL}/citas/reservar", json={
    "cedula": "0987654321",
    "nombres": "María García",
    "correo": "maria@email.com", 
    "telefono": "0991234567",
    "fecha": "2024-01-16",
    "hora": "14:30:00",
    "motivo": "Chequeo anual"
}).json()

print(f"✅ Cita reservada ID: {nueva_cita['id']}")
print(f"📅 Fecha: {nueva_cita['fecha']} {nueva_cita['hora']}")
```

## 🔒 Seguridad

### Características de Seguridad Implementadas

- **Autenticación JWT**: Tokens seguros con expiración (30 minutos)
- **Validación de cédula**: Algoritmo de validación ecuatoriana
- **Hashing de contraseñas**: bcrypt para almacenamiento seguro
- **Validación de datos**: Pydantic para validación estricta
- **CORS configurado**: Control de acceso desde frontends
- **Pool de conexiones**: Previene ataques de agotamiento
- **Logging de seguridad**: Registro de intentos de login

### Recomendaciones de Producción

1. **SECRET_KEY fuerte**: Generar clave de 256 bits para JWT
2. **HTTPS obligatorio**: Certificados SSL/TLS en producción
3. **Firewall PostgreSQL**: Restringir acceso solo desde la aplicación
4. **Rate limiting**: Implementar límites de peticiones
5. **Backup automático**: Configurar respaldos diarios de BD
6. **Monitoreo**: Logs centralizados y alertas

## 🐛 Solución de Problemas

### Problemas Comunes

#### Error de Conexión a PostgreSQL
```
❌ Error conectando a PostgreSQL: connection refused
```
**Solución**: 
- Verificar que PostgreSQL esté ejecutándose
- Comprobar IP, puerto y credenciales en `.env`
- Verificar firewall y conectividad de red

#### Token JWT Inválido
```
401 Unauthorized: No se pudieron validar las credenciales
```
**Solución**: 
- Token expirado (válido 30 minutos) → hacer login nuevamente
- Header Authorization mal formateado → usar `Bearer {token}`
- SECRET_KEY diferente → verificar consistency

#### Cédula Inválida
```
400 Bad Request: Cédula inválida
```
**Solución**: 
- Cédula debe tener exactamente 10 dígitos
- Debe pasar algoritmo de validación ecuatoriana
- No usar cédulas ficticias como "1234567890"

#### Conflicto de Horarios
```
400 Bad Request: Ya existe una cita programada para esa fecha y hora
```
**Solución**: 
- El sistema previene double-booking
- Verificar agenda antes de agendar
- Usar horarios diferentes

#### Pool de Conexiones Agotado
```
❌ Error: Pool de base de datos no inicializado
```
**Solución**: 
- Reiniciar la aplicación
- Verificar que PostgreSQL acepte conexiones
- Revisar logs de base de datos

### Logs Útiles

```bash
# Ver logs de la aplicación
# Los logs aparecen en la consola donde ejecutas uvicorn

# Verificar conexión a BD
curl http://localhost:8000/health

# Ver documentación
curl http://localhost:8000/docs
```

### Health Check

```bash
curl http://localhost:8000/health
```

Respuesta exitosa:
```json
{
  "status": "healthy",
  "database": "connected", 
  "message": "Aplicación funcionando correctamente"
}
```

### Comandos de Verificación

```bash
# Verificar que la aplicación inicie
uvicorn main:app --reload

# Probar endpoint público
curl -X POST http://localhost:8000/pacientes/ \
  -H "Content-Type: application/json" \
  -d '{"cedula":"1234567890","nombres":"Test User","correo":"test@test.com","telefono":"0999999999"}'

# Probar login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"medico","password":"medico123"}'
```

## 🚀 Despliegue

### Producción Local

```bash
# Con Gunicorn para producción
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Variables de Producción

```env
# .env para producción
POSTGREST_URL=tu-ip-produccion
DB_PORT=5432
DB_USER=clinica_user
DB_PASSWORD=contraseña-muy-segura
DB_NAME=clinica_prod
SECRET_KEY=clave-jwt-de-256-bits-super-segura
LOG_LEVEL=WARNING
```

## 📊 Monitoreo

### Métricas Importantes

- **Conexiones activas**: Pool de PostgreSQL
- **Tiempo de respuesta**: Endpoints críticos
- **Errores 5xx**: Fallos del servidor
- **Intentos de login**: Seguridad
- **Uso de memoria**: Aplicación Python

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/NuevaFuncionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/NuevaFuncionalidad`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Autor

Desarrollado para sistema de clínica médica con arquitectura moderna y separación clara entre funcionalidades públicas y privadas.

---

**🩺 ¿Necesitas ayuda?** 
- Revisa la documentación interactiva en `/docs`
- Verifica el health check en `/health`
- Consulta los logs de la consola para errores específicos 