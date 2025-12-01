"""External service integrations for Telemetry context."""
import os
import requests
from typing import Optional, Dict, Any
from telemetry.domain.entities import SensorReading


class SafeCarBackendService:
    """Service for integrating with SafeCar backend platform.

    Sends telemetry samples to the backend for processing,
    mapping ESP32 sensor data to backend TelemetrySample structure.
    """

    def __init__(self):
        """Initialize the SafeCar backend service with configuration."""
        # Backend URL (configurable via env BACKEND_URL)
        self.backend_url = os.getenv('BACKEND_URL', 'https://safecar.joyeria-sharvel.com')
        self.telemetry_endpoint = f"{self.backend_url}/api/v1/telemetry"
        self.timeout = 10  # seconds

    def send_telemetry_sample(
        self,
        reading: SensorReading,
        telemetry_type: str,
        severity: str
    ) -> bool:
        """Send a telemetry sample to the SafeCar backend.

        Maps ESP32 sensor data to backend CreateTelemetryResource (FLAT structure):
        - cabin_temperature_celsius → cabinTemperature (Double)
        - engine_temperature_celsius → engineTemperature (Double)
        - cabin_humidity_percent → cabinHumidity (Double)
        - latitude, longitude → latitude, longitude (Double, Double)
        - gas_type → cabinGasType (String enum: METHANE, PROPANE, etc.)
        - gas_concentration_ppm → cabinGasConcentration (Double)
        - current_amperes → electricalCurrent (Double)

        Args:
            reading: Sensor reading to send.
            telemetry_type: Type of telemetry (e.g., CABIN_GAS).
            severity: Alert severity (INFO, WARN, CRITICAL).

        Returns:
            bool: True if sent successfully, False otherwise.
        """
        try:
            payload = self._build_telemetry_payload(reading, telemetry_type, severity)

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(
                self.telemetry_endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code == 201:
                return True
            else:
                print(f"Failed to send telemetry: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except requests.RequestException as e:
            print(f"Error sending telemetry to backend: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error sending telemetry: {str(e)}")
            return False

    def _build_telemetry_payload(
        self,
        reading: SensorReading,
        telemetry_type: str,
        severity: str
    ) -> Dict[str, Any]:
        """Build the telemetry payload compatible with SafeCar backend.

        Backend expects a FLAT structure (CreateTelemetryResource) with the
        device MAC address instead of vehicle/driver identifiers:
        {
            "macAddress": "AA:BB:CC:DD:EE:FF",
            "type": "CABIN_GAS",
            "severity": "WARN",
            "timestamp": "2025-11-27T20:00:00Z",
            "cabinTemperature": 25.5,
            "cabinHumidity": 65.0,
            "cabinGasType": "METHANE",
            "cabinGasConcentration": 450.0,
            "latitude": -12.0464,
            "longitude": -77.0428,
            "engineTemperature": 95.0,
            "electricalCurrent": 2.5
        }

        Args:
            reading: Sensor reading.
            telemetry_type: Telemetry type.
            severity: Alert severity.

        Returns:
            Dict: Flat telemetry payload matching CreateTelemetryResource.
        """
        # Build FLAT payload structure
        payload = {
            "macAddress": reading.device_id,
            "type": telemetry_type,
            "severity": severity,
            "timestamp": reading.timestamp.isoformat()
        }

        # Add cabin temperature (DHT11 from CABINA) - flat field
        if reading.has_cabin_temperature_reading():
            payload["cabinTemperature"] = reading.cabin_temperature_celsius

        # Add engine temperature (DHT11 from MOTOR) - flat field
        if reading.has_engine_temperature_reading():
            payload["engineTemperature"] = reading.engine_temperature_celsius

        # Add cabin humidity (DHT11 from CABINA) - flat field
        if reading.has_cabin_humidity_reading():
            payload["cabinHumidity"] = reading.cabin_humidity_percent

        # Add gas detection (MQ2 from CABINA) - flat fields
        if reading.has_gas_reading():
            # Map MQ2 gas types to backend CabinGasType enum
            # Backend accepts: CO2, CO, FUEL_VAPOR, SMOKE, UNKNOWN
            # MQ2 detects combustible gases (methane, propane, butane, etc.)
            # Map all MQ2 detections to FUEL_VAPOR (most appropriate for combustible gases)
            gas_type_mapping = {
                'methane': 'FUEL_VAPOR',
                'propane': 'FUEL_VAPOR',
                'butane': 'FUEL_VAPOR',
                'lpg': 'FUEL_VAPOR',
                'alcohol': 'FUEL_VAPOR',
                'hydrogen': 'FUEL_VAPOR',
                'smoke': 'SMOKE',
                'co': 'CO',
                'co2': 'CO2'
            }
            backend_gas_type = gas_type_mapping.get(
                reading.gas_type.lower(),
                'UNKNOWN'  # Default fallback
            )

            payload["cabinGasType"] = backend_gas_type
            payload["cabinGasConcentration"] = reading.gas_concentration_ppm

        # Add GPS location (NEO6M from CABINA) - flat fields
        if reading.has_gps_reading():
            payload["latitude"] = reading.latitude
            payload["longitude"] = reading.longitude

        # Add electrical current (ACS712 from MOTOR) - flat field
        if reading.has_current_reading():
            payload["electricalCurrent"] = reading.current_amperes

        return payload

    def test_connection(self) -> bool:
        """Test connection to SafeCar backend.

        Returns:
            bool: True if backend is reachable.
        """
        try:
            response = requests.get(
                f"{self.backend_url}/actuator/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
