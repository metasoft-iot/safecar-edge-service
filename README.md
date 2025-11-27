# SafeCar Edge Service

Edge service para la recolección y procesamiento de datos de sensores IoT vehiculares desde dos dispositivos ESP32, integrado con la plataforma SafeCar.

## Descripción

Este servicio actúa como intermediario entre los dispositivos IoT instalados en vehículos y el backend de SafeCar. Procesa datos de múltiples sensores en tiempo real desde dos ESP32 ubicados en diferentes puntos del vehículo, normaliza la información y la envía al sistema central para análisis predictivo y generación de alertas.

## Dispositivos y Sensores

### ESP32 (CABINA) - Ubicado en la cabina del vehículo

#### 1. DHT11 - Sensor de Temperatura y Humedad
- **Función**: Monitoreo de temperatura y humedad en cabina
- **Rango Temperatura**: 0°C a +50°C
- **Rango Humedad**: 20% a 90%
- **Precisión**: ±2°C, ±5%
- **Aplicación**: Confort del conductor, detección de condiciones anormales

#### 2. MQ2 - Sensor de Gases
- **Gases detectados**: GLP, i-butano, propano, metano, alcohol, hidrógeno
- **Rango**: 300-10,000 ppm
- **Aplicación**: Detección de fugas de gas, monitoreo de calidad del aire, alertas de seguridad

#### 3. NEO6M - Módulo GPS
- **Tipo**: Receptor GPS con EEPROM y antena de recepción
- **Precisión**: ~2.5 metros CEP
- **Aplicación**: Seguimiento de ubicación del vehículo, registro de rutas

### ESP32 (MOTOR) - Ubicado en el compartimento del motor

#### 1. DHT11 - Sensor de Temperatura y Humedad
- **Función**: Monitoreo de temperatura y humedad en motor
- **Rango**: Ver especificaciones arriba
- **Aplicación**: Detección de sobrecalentamiento, monitoreo de condiciones del motor

#### 2. ACS712-05 - Sensor de Corriente
- **Tipo**: Sensor de efecto Hall
- **Rango**: 0-5 Amperios
- **Aplicación**: Monitoreo del sistema eléctrico, detección de fallas en batería y alternador

## Arquitectura

El proyecto sigue Domain-Driven Design (DDD) con la siguiente estructura de bounded contexts:

```
safecar-edge-service/
├── iam/                    # Identity & Access Management
│   ├── application/        # Application services
│   ├── domain/            # Entities, value objects, services
│   ├── infrastructure/    # Repositories, models (Peewee ORM)
│   └── interfaces/        # REST API controllers
├── telemetry/             # Telemetry collection and processing
│   ├── application/       # Application services
│   ├── domain/           # Entities, value objects, services
│   ├── infrastructure/   # Repositories, models, external services
│   └── interfaces/       # REST API controllers
└── shared/               # Shared infrastructure
    └── infrastructure/   # Database, configuration
```

## Instalación

### Requisitos previos
- Python 3.8+
- pip

### Pasos de instalación

1. Clonar el repositorio:
```bash
cd /Volumes/Workspace/GitHub/Organizations/metasoft-iot/safecar-edge-service
```

2. Crear entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

El servicio está configurado para funcionar localmente sin necesidad de archivos `.env`:

- **Backend URL**: `http://localhost:8080` (hardcoded)
- **Vehicle ID**: `1` (hardcoded)
- **Driver ID**: `1` (hardcoded)
- **Device ID**: `safecar-001` (creado automáticamente)
- **API Key**: `test-api-key-12345` (creado automáticamente)

> **Nota**: Para producción, estos valores se pueden extraer a variables de entorno, pero para desarrollo local no es necesario.

## Uso

### Prerrequisitos para Operación Completa

Para que el sistema SafeCar funcione de extremo a extremo, necesitas:

#### 1. Backend SafeCar (Obligatorio)
```bash
# El backend debe estar corriendo en http://localhost:8080
cd /path/to/safecar-backend
./mvnw spring-boot:run
```

#### 2. Base de Datos Backend (MySQL)
```bash
# El backend requiere MySQL corriendo
# Configurado en application.properties del backend
```

#### 3. Edge Service (Este proyecto)
```bash
# Debe estar corriendo en http://localhost:5000
python app.py
```

#### 4. Dispositivos IoT (ESP32) o Simulador
- **Opción A**: ESP32 físicos programados con código Arduino
- **Opción B**: Script simulador para pruebas: `python simulate_sensors.py`

---

## Cómo Funciona la Integración Backend-Edge-IoT

### Arquitectura de Flujo de Datos

```
┌──────────────────────────────────────────────────────────────┐
│                    CAPA DE APLICACIÓN                         │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  SafeCar Web Dashboard / Workshop Interface         │     │
│  │  - Ver telemetría en tiempo real                    │     │
│  │  - Insights generados por IA                        │     │
│  │  - Alertas de mantenimiento                         │     │
│  └──────────────────────┬──────────────────────────────┘     │
└─────────────────────────┼────────────────────────────────────┘
                          │ REST API
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                    BACKEND (Spring Boot)                      │
│                   http://localhost:8080                       │
│                                                               │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────┐  │
│  │ Telemetry      │  │ Insights        │  │ Workshop     │  │
│  │ Context        │  │ Context (IA)    │  │ Context      │  │
│  └────────────────┘  └─────────────────┘  └──────────────┘  │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐     │
│  │         MySQL Database                               │     │
│  │  - telemetry_records                                 │     │
│  │  - vehicle_insights                                  │     │
│  │  - vehicle_telemetries                               │     │
│  └─────────────────────────────────────────────────────┘     │
└──────────────────────────┬────────────────────────────────────┘
                           │ HTTP POST
                           │ /api/v1/telemetry
                           ▼
┌──────────────────────────────────────────────────────────────┐
│              EDGE SERVICE (Flask) - Este Proyecto             │
│                   http://localhost:5000                       │
│                                                               │
│  ┌────────────────────────────────────────────────────┐      │
│  │  IAM Context          │  Telemetry Context         │      │
│  │  - Autenticación      │  - Validación de datos     │      │
│  │  - Device mgmt        │  - Normalización           │      │
│  │                       │  - Mapping a TelemetrySample│     │
│  └────────────────────────────────────────────────────┘      │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐     │
│  │         SQLite Local Database                        │     │
│  │  - devices (IAM)                                     │     │
│  │  - sensor_readings (cache local)                     │     │
│  └─────────────────────────────────────────────────────┘     │
└──────────────────────────┬────────────────────────────────────┘
                           │ HTTP POST
                           │ /api/v1/telemetry/samples
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                  DISPOSITIVOS IoT (ESP32)                     │
│                                                               │
│  ┌─────────────────────────┐  ┌─────────────────────────┐   │
│  │   ESP32 (CABINA)        │  │   ESP32 (MOTOR)         │   │
│  │   - DHT11 (temp/hum)    │  │   - DHT11 (temp/hum)    │   │
│  │   - MQ2 (gas)           │  │   - ACS712 (corriente)  │   │
│  │   - NEO6M GPS           │  │                         │   │
│  └─────────────────────────┘  └─────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### Flujo de Operación Paso a Paso

#### 1️⃣ **Registro Automático de Dispositivos**

Al iniciar el Edge Service por primera vez:

```python
# En app.py - se ejecuta automáticamente
@app.before_request
def setup():
    # Crea la base de datos SQLite local
    initialize_database()
    
    # Crea dispositivo de prueba automáticamente
    device = auth_service.get_or_create_test_device()
    # device_id: "safecar-001"
    # api_key: "test-api-key-12345"
```

**No necesitas registrar manualmente el dispositivo** - se crea automáticamente en la primera ejecución.

#### 2️⃣ **Envío de Datos desde ESP32/Simulador**

```
[ESP32] Lee sensores cada 5 segundos
   ↓
[ESP32] Crea JSON con datos:
   {
     "sensor_location": "CABINA",
     "cabin_temperature_celsius": 25.5,
     "cabin_humidity_percent": 65.0,
     "gas_type": "methane",
     "gas_concentration_ppm": 150.0,
     "latitude": -12.0464,
     "longitude": -77.0428
   }
   ↓
[ESP32] Envía POST a Edge Service:
   URL: http://192.168.1.XX:5000/api/v1/telemetry/samples
   Headers:
     - X-Device-Id: safecar-001
     - X-API-Key: test-api-key-12345
     - Content-Type: application/json
```

#### 3️⃣ **Procesamiento en Edge Service**

```
[Edge] Recibe POST /api/v1/telemetry/samples
   ↓
[Edge IAM] Valida device_id y api_key
   ↓
[Edge Telemetry] Valida datos de sensores:
   - Rangos de temperatura (-40°C a 80°C)
   - Rangos de humedad (0% a 100%)
   - Coordenadas GPS válidas
   - Valores de gas y corriente
   ↓
[Edge Domain] Determina severidad:
   - INFO: Valores normales
   - WARNING: Valores en rango de alerta
   - CRITICAL: Valores peligrosos
   ↓
[Edge Domain] Determina tipo de telemetría:
   - CABIN_GAS_DETECTED
   - ENGINE_OVERHEAT
   - TEMPERATURE_ANOMALY
   - LOCATION_UPDATE
   - ELECTRICAL_FAULT
   ↓
[Edge Repository] Guarda en SQLite local (backup)
   ↓
[Edge External Service] Mapea a formato TelemetrySample:
   {
     "sample": {
       "type": "CABIN_GAS_DETECTED",
       "severity": "WARNING",
       "vehicleId": {"vehicleId": 1},
       "driverId": {"driverId": 1},
       "cabinTemperature": {"value": 25.5},
       "cabinHumidity": {"value": 65.0},
       "cabinGasLevel": {
         "type": "METHANE",
         "concentrationPpm": 150.0
       },
       "location": {
         "latitude": -12.0464,
         "longitude": -77.0428
       }
     }
   }
   ↓
[Edge] Envía a Backend:
   POST http://localhost:8080/api/v1/telemetry
```

#### 4️⃣ **Procesamiento en Backend**

```
[Backend] Recibe telemetría
   ↓
[Backend Workshop] Crea TelemetryRecord
   ↓
[Backend Workshop] Guarda en MySQL:
   - telemetry_records
   - Actualiza vehicle_telemetries.record_count
   ↓
[Backend Events] Emite TelemetrySampleIngestedEvent
   ↓
[Backend Insights] Escucha evento
   ↓
[Backend Insights] Genera insight con IA (Gemini):
   - Analiza patrón de sensores
   - Detecta anomalías
   - Genera recomendaciones
   ↓
[Backend Insights] Guarda VehicleInsight en BD
```

#### 5️⃣ **Visualización en Dashboard**

```
[Usuario] Accede a Dashboard Web
   ↓
[Dashboard] GET /api/v1/telemetry/vehicles/{vehicleId}
   ↓
[Dashboard] Muestra:
   - Telemetría en tiempo real
   - Gráficas de temperatura, gas, corriente
   - Ubicación GPS en mapa
   ↓
[Dashboard] GET /api/v1/insights/vehicles/{vehicleId}
   ↓
[Dashboard] Muestra insights de IA:
   - Alertas de mantenimiento
   - Predicciones
   - Recomendaciones
```

---

## Conectar Dispositivos IoT Reales

### Opción 1: Usar Simulador (Para Desarrollo/Pruebas)

```bash
# Terminal 1: Backend
cd /path/to/safecar-backend
./mvnw spring-boot:run

# Terminal 2: Edge Service
cd /path/to/safecar-edge-service
python app.py

# Terminal 3: Simulador
python simulate_sensors.py
```

El simulador enviará datos alternados de CABINA y MOTOR cada 5 segundos.

### Opción 2: Conectar ESP32 Real

#### Paso 1: Programar ESP32

Usa el código Arduino de la guía de integración (`guia_integracion.md`) para:
- ESP32 (CABINA): DHT11 + MQ2 + NEO6M GPS
- ESP32 (MOTOR): DHT11 + ACS712

#### Paso 2: Configurar WiFi en ESP32

```cpp
// En el código Arduino
const char* ssid = "TU_RED_WIFI";
const char* password = "TU_PASSWORD_WIFI";
```

#### Paso 3: Configurar IP del Edge Service

```cpp
// Obtén la IP del Edge Service
// Se muestra al iniciar: "Running on http://192.168.1.XX:5000"

const char* edgeServiceURL = "http://192.168.1.XX:5000/api/v1/telemetry/samples";
```

#### Paso 4: Usar Credenciales del Dispositivo

```cpp
// Estas credenciales se crean automáticamente en el Edge Service
const char* deviceId = "safecar-001";
const char* apiKey = "test-api-key-12345";
```

#### Paso 5: Verificar Envío

Deberías ver en el Serial Monitor del ESP32:
```
WiFi connected
Data sent successfully: 201
{"message": "Sensor reading recorded successfully", ...}
```

### Opción 3: Crear Nuevos Dispositivos

Si necesitas múltiples dispositivos (ej: múltiples vehículos):

**Método 1 - Vía Código:**
```python
# En iam/infrastructure/repositories.py
device_model, _ = DeviceModel.get_or_create(
    device_id="safecar-002",  # Nuevo ID
    defaults={
        "api_key": "new-api-key-67890",
        "created_at": datetime.now(timezone.utc)
    }
)
```

**Método 2 - Vía SQLite:**
```bash
sqlite3 safecar_edge.db
INSERT INTO devices (device_id, api_key, created_at) 
VALUES ('safecar-002', 'new-api-key-67890', datetime('now'));
```

---

## Verificación de Funcionamiento

### 1. Verificar Backend está corriendo

```bash
curl http://localhost:8080/actuator/health
# Debería retornar: {"status":"UP"}
```

### 2. Verificar Edge Service está corriendo

```bash
curl http://localhost:5000/
# Debería retornar: Welcome to SafeCar Edge Service
```

### 3. Enviar dato de prueba manual

```bash
curl -X POST http://localhost:5000/api/v1/telemetry/samples \
  -H "Content-Type: application/json" \
  -H "X-Device-Id: safecar-001" \
  -H "X-API-Key: test-api-key-12345" \
  -d '{
    "sensor_location": "CABINA",
    "cabin_temperature_celsius": 25.0,
    "cabin_humidity_percent": 60.0,
    "timestamp": "2025-11-26T18:30:00Z"
  }'
```

Deberías recibir:
```json
{
  "message": "Sensor reading recorded successfully",
  "data": {
    "id": 1,
    "backend_synced": true,
    "severity": "INFO",
    "telemetry_type": "TEMPERATURE_ANOMALY"
  }
}
```

### 4. Verificar datos en Backend

```bash
# Acceder a MySQL del backend
mysql -u root -p safecar_db

# Consultar telemetría recibida
SELECT id, sample_cabin_temp_c, sample_cabin_humidity_percent, 
       telemetry_type, alert_severity, created_at 
FROM telemetry_records 
ORDER BY id DESC LIMIT 5;
```

### 5. Verificar Insights generados

```bash
# Consultar insights
SELECT id, vehicle_id, description, recommendation, 
       generated_at 
FROM vehicle_insights 
ORDER BY id DESC LIMIT 5;
```

---

## Iniciar el servicio

```bash
python app.py
```

El servicio estará disponible en `http://localhost:5000`

### Endpoints disponibles

#### 1. Health Check
```bash
GET /
```

#### 2. Enviar muestra de telemetría - ESP32 (CABINA)
```bash
POST /api/v1/telemetry/samples
Content-Type: application/json
X-Device-Id: safecar-001
X-API-Key: test-api-key-12345

{
  "sensor_location": "CABINA",
  "cabin_temperature_celsius": 25.5,
  "cabin_humidity_percent": 65.0,
  "gas_type": "methane",
  "gas_concentration_ppm": 150.0,
  "latitude": -12.0464,
  "longitude": -77.0428,
  "timestamp": "2025-11-26T18:30:00Z"
}
```

#### 3. Enviar muestra de telemetría - ESP32 (MOTOR)
```bash
POST /api/v1/telemetry/samples
Content-Type: application/json
X-Device-Id: safecar-001
X-API-Key: test-api-key-12345

{
  "sensor_location": "MOTOR",
  "engine_temperature_celsius": 95.0,
  "engine_humidity_percent": 45.0,
  "current_amperes": 2.5,
  "timestamp": "2025-11-26T18:30:00Z"
}
```

#### 4. Obtener estadísticas locales
```bash
GET /api/v1/telemetry/stats
X-Device-Id: safecar-001
X-API-Key: test-api-key-12345
```

#### 5. Obtener lecturas por vehículo
```bash
GET /api/v1/telemetry/vehicles/{vehicle_id}/readings?limit=50
```

## Integración con SafeCar Backend

Este edge service se integra con el backend de SafeCar mediante:

1. **Autenticación**: Validación de dispositivos mediante IAM
2. **Telemetría**: Envío de muestras al endpoint `/api/v1/telemetry`
3. **Normalización**: Transformación de datos de sensores al formato `TelemetrySample`

### Mapeo de sensores a tipos de telemetría

| Sensor ESP32 | Campo Edge Service | Campo Backend | TelemetryType |
|--------------|-------------------|---------------|---------------|
| DHT11 (CABINA) | `cabin_temperature_celsius` | `sample.cabinTemperature` | TEMPERATURE_ANOMALY |
| DHT11 (CABINA) | `cabin_humidity_percent` | `sample.cabinHumidity` | TEMPERATURE_ANOMALY |
| DHT11 (MOTOR) | `engine_temperature_celsius` | `sample.engineTemperature` | ENGINE_OVERHEAT |
| DHT11 (MOTOR) | `engine_humidity_percent` | - | - |
| MQ2 (CABINA) | `gas_type`, `gas_concentration_ppm` | `sample.cabinGasLevel` | CABIN_GAS_DETECTED |
| NEO6M (CABINA) | `latitude`, `longitude` | `sample.location` (GeoPoint) | LOCATION_UPDATE |
| ACS712 (MOTOR) | `current_amperes` | `sample.electricalCurrent` | ELECTRICAL_FAULT |

## Desarrollo

### Ejecutar en modo desarrollo

```bash
export FLASK_ENV=development
python app.py
```

### Simulación de sensores

Para probar el sistema sin hardware físico:

```bash
python simulate_sensors.py
```

Este script simula lecturas alternadas de ambos ESP32:
- Lecturas impares: ESP32 (CABINA) con DHT11, MQ2, GPS
- Lecturas pares: ESP32 (MOTOR) con DHT11, ACS712

## Arquitectura del Sistema

```
┌─────────────────────────────────────────┐
│      SafeCar Backend Platform           │
│  (Telemetry Processing & Insights)      │
└──────────────────┬──────────────────────┘
                   │ HTTP/JSON
                   │ /api/v1/telemetry
┌──────────────────▼──────────────────────┐
│      SafeCar Edge Service               │
│  (Data Normalization & Local Storage)   │
│                                          │
│  ┌────────────┐    ┌─────────────────┐  │
│  │ IAM        │    │ Telemetry       │  │
│  │ Context    │    │ Context         │  │
│  └────────────┘    └─────────────────┘  │
└──────────────────┬──────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
┌────────▼────────┐  ┌───────▼────────┐
│  ESP32 (CABINA) │  │ ESP32 (MOTOR)  │
│  - DHT11        │  │ - DHT11        │
│  - MQ2          │  │ - ACS712-05    │
│  - NEO6M GPS    │  │                │
└─────────────────┘  └────────────────┘
```

## Contribución

Este proyecto es parte de la plataforma SafeCar desarrollada por MetaSoft IoT siguiendo los patrones de Domain-Driven Design enseñados en el curso.

## Licencia

MIT License

## Contacto

Para más información sobre SafeCar, visita el repositorio principal del backend.
