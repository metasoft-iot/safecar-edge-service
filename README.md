# SafeCar Edge Service

Edge service para la recolección y procesamiento de datos de sensores IoT vehiculares, integrado con la plataforma SafeCar.

## Descripción

Este servicio actúa como intermediario entre los dispositivos IoT instalados en vehículos y el backend de SafeCar. Procesa datos de múltiples sensores en tiempo real, normaliza la información y la envía al sistema central para análisis predictivo y generación de alertas.

## Sensores Soportados

### 1. LM35 - Sensor de Temperatura
- **Función**: Monitoreo de temperatura de cabina y motor
- **Rango**: -55°C a +150°C
- **Precisión**: ±0.5°C
- **Aplicación**: Detección de sobrecalentamiento del motor, confort de cabina

### 2. MQ2 - Sensor de Gases
- **Gases detectados**: GLP, i-butano, propano, metano, alcohol, hidrógeno
- **Rango**: 300-10,000 ppm
- **Aplicación**: Detección de fugas de gas, monitoreo de calidad del aire en cabina, alertas de seguridad

### 3. ACS712-05 - Sensor de Corriente
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
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## Configuración

Crear archivo `.env` con las siguientes variables:

```env
# SafeCar Backend Configuration
SAFECAR_BACKEND_URL=http://localhost:8080
SAFECAR_BACKEND_API_KEY=your-api-key-here

# Device Configuration
VEHICLE_ID=1
DRIVER_ID=1
DEVICE_ID=edge-device-001
DEVICE_API_KEY=your-device-api-key

# Sensor Configuration
TEMPERATURE_SENSOR_PIN=A0
GAS_SENSOR_PIN=A1
CURRENT_SENSOR_PIN=A2

# Sampling Configuration
SAMPLE_INTERVAL_SECONDS=5
BATCH_SIZE=10
```

## Uso

### Iniciar el servicio

```bash
python app.py
```

El servicio estará disponible en `http://localhost:5000`

### Endpoints disponibles

#### 1. Health Check
```bash
GET /
```

#### 2. Autenticación de dispositivo
```bash
POST /api/v1/auth/devices
Content-Type: application/json

{
  "device_id": "edge-device-001",
  "api_key": "your-api-key"
}
```

#### 3. Enviar muestra de telemetría
```bash
POST /api/v1/telemetry/samples
Content-Type: application/json
X-Device-Id: edge-device-001
X-API-Key: your-api-key

{
  "temperature_celsius": 85.5,
  "gas_type": "methane",
  "gas_concentration_ppm": 450.0,
  "current_amperes": 2.3,
  "timestamp": "2025-11-13T10:30:00Z"
}
```

#### 4. Obtener estadísticas locales
```bash
GET /api/v1/telemetry/stats
X-Device-Id: edge-device-001
X-API-Key: your-api-key
```

## Integración con SafeCar Backend

Este edge service se integra con el backend de SafeCar mediante:

1. **Autenticación**: Validación de dispositivos mediante IAM
2. **Telemetría**: Envío de muestras al endpoint `/api/v1/telemetry`
3. **Normalización**: Transformación de datos de sensores al formato `TelemetrySample`

### Mapeo de sensores a tipos de telemetría

| Sensor | TelemetryType | Campos relacionados |
|--------|---------------|-------------------|
| LM35 | TEMPERATURE | - (extensión futura) |
| MQ2 | CABIN_GAS_DETECTED | cabinGasLevel.type, cabinGasLevel.concentrationPpm |
| ACS712-05 | ELECTRICAL_FAULT | - (extensión futura) |

## Desarrollo

### Ejecutar en modo desarrollo

```bash
export FLASK_ENV=development
python app.py
```

### Tests

```bash
python -m pytest tests/
```

## Contribución

Este proyecto es parte de la plataforma SafeCar desarrollada por MetaSoft IoT.

## Licencia

MIT License

## Contacto

Para más información sobre SafeCar, visita el repositorio principal del backend.
