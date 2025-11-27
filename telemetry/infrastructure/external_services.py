"""External service integrations for Telemetry context."""
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
        # Backend URL (local por ahora, sin .env)
        self.backend_url = 'http://localhost:8080'
        self.telemetry_endpoint = f"{self.backend_url}/api/v1/telemetry"
        self.timeout = 10  # seconds

    def send_telemetry_sample(
        self,
        reading: SensorReading,
        telemetry_type: str,
        severity: str
    ) -> bool:
        """Send a telemetry sample to the SafeCar backend.

        Maps ESP32 sensor data to backend TelemetrySample structure:
        - cabin_temperature_celsius → sample.cabinTemperature
        - engine_temperature_celsius → sample.engineTemperature
        - cabin_humidity_percent → sample.cabinHumidity
        - latitude, longitude → sample.location (GeoPoint)
        - gas_type, gas_concentration_ppm → sample.cabinGasLevel
        - current_amperes → sample.electricalCurrent

        Args:
            reading: Sensor reading to send.
            telemetry_type: Type of telemetry (e.g., CABIN_GAS_DETECTED).
            severity: Alert severity (INFO, WARNING, CRITICAL).

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

        Args:
            reading: Sensor reading.
            telemetry_type: Telemetry type.
            severity: Alert severity.

        Returns:
            Dict: Telemetry payload matching IngestTelemetrySampleCommand.
        """
        # Build the TelemetrySample structure
        sample = {
            "type": telemetry_type,
            "severity": severity,
            "timestamp": {
                "occurredAt": reading.timestamp.isoformat()
            },
            "vehicleId": {
                "vehicleId": reading.vehicle_id
            },
            "driverId": {
                "driverId": reading.driver_id
            }
        }

        # Map cabin temperature (DHT11 from CABINA)
        if reading.has_cabin_temperature_reading():
            sample["cabinTemperature"] = {
                "value": reading.cabin_temperature_celsius
            }

        # Map engine temperature (DHT11 from MOTOR)
        if reading.has_engine_temperature_reading():
            sample["engineTemperature"] = {
                "value": reading.engine_temperature_celsius
            }

        # Map cabin humidity (DHT11 from CABINA)
        if reading.has_cabin_humidity_reading():
            sample["cabinHumidity"] = {
                "value": reading.cabin_humidity_percent
            }

        # Map gas detection (MQ2 from CABINA)
        if reading.has_gas_reading():
            # Map gas type to CabinGasType enum
            gas_type_mapping = {
                'methane': 'METHANE',
                'propane': 'PROPANE',
                'butane': 'BUTANE',
                'alcohol': 'ALCOHOL',
                'hydrogen': 'HYDROGEN',
                'lpg': 'LPG'
            }
            backend_gas_type = gas_type_mapping.get(
                reading.gas_type.lower(),
                'OTHER'
            )

            sample["cabinGasLevel"] = {
                "type": backend_gas_type,
                "concentrationPpm": reading.gas_concentration_ppm
            }

        # Map GPS location (NEO6M from CABINA)
        if reading.has_gps_reading():
            sample["location"] = {
                "latitude": reading.latitude,
                "longitude": reading.longitude
            }

        # Map electrical current (ACS712 from MOTOR)
        if reading.has_current_reading():
            sample["electricalCurrent"] = {
                "value": reading.current_amperes
            }

        # Wrap in IngestTelemetrySampleCommand structure
        payload = {
            "sample": sample
        }

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
