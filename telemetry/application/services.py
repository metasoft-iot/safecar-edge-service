"""Application services for Telemetry context."""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from dateutil.parser import parse

from telemetry.domain.entities import SensorReading
from telemetry.domain.services import SensorReadingService
from telemetry.infrastructure.repositories import SensorReadingRepository
from telemetry.infrastructure.external_services import SafeCarBackendService
from iam.application.services import AuthApplicationService


class TelemetryApplicationService:
    """Application service for managing telemetry operations.

    Coordinates between domain logic, persistence, and external services
    for sensor data from ESP32 devices (CABINA and MOTOR).
    """

    def __init__(self):
        """Initialize the TelemetryApplicationService with necessary dependencies."""
        self.sensor_reading_repository = SensorReadingRepository()
        self.sensor_reading_service = SensorReadingService()
        self.backend_service = SafeCarBackendService()
        self.iam_service = AuthApplicationService()

    def record_sensor_reading(
        self,
        device_id: str,
        api_key: str,
        sensor_location: Optional[str] = None,
        cabin_temperature_celsius: Optional[float] = None,
        cabin_humidity_percent: Optional[float] = None,
        engine_temperature_celsius: Optional[float] = None,
        engine_humidity_percent: Optional[float] = None,
        gas_type: Optional[str] = None,
        gas_concentration_ppm: Optional[float] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        current_amperes: Optional[float] = None,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record a new sensor reading and send to backend.

        Args:
            device_id: Device identifier.
            api_key: API key for authentication.
            sensor_location: Sensor location ('CABINA' or 'MOTOR').
            cabin_temperature_celsius: Temperature from CABINA DHT11.
            cabin_humidity_percent: Humidity from CABINA DHT11.
            engine_temperature_celsius: Temperature from MOTOR DHT11.
            engine_humidity_percent: Humidity from MOTOR DHT11.
            gas_type: Type of gas detected by MQ2.
            gas_concentration_ppm: Gas concentration.
            latitude: GPS latitude from NEO6M.
            longitude: GPS longitude from NEO6M.
            current_amperes: Current from ACS712.
            timestamp: ISO format timestamp.

        Returns:
            Dict: Result with reading ID and backend sync status.

        Raises:
            ValueError: If authentication fails or data is invalid.
        """
        # Authenticate device
        device = self.iam_service.get_device_by_id_and_api_key(device_id, api_key)
        if not device:
            raise ValueError("Device not found or invalid API key")

        # Vehicle and driver IDs hardcoded para simplicidad (local)
        vehicle_id = 1
        driver_id = 1

        # Create sensor reading using domain service
        reading = self.sensor_reading_service.create_sensor_reading(
            device_id=device_id,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            sensor_location=sensor_location,
            cabin_temperature_celsius=cabin_temperature_celsius,
            cabin_humidity_percent=cabin_humidity_percent,
            engine_temperature_celsius=engine_temperature_celsius,
            engine_humidity_percent=engine_humidity_percent,
            gas_type=gas_type,
            gas_concentration_ppm=gas_concentration_ppm,
            latitude=latitude,
            longitude=longitude,
            current_amperes=current_amperes,
            timestamp=timestamp
        )

        # Save to local database
        saved_reading = self.sensor_reading_repository.save(reading)

        # Determine telemetry metadata
        severity = self.sensor_reading_service.determine_alert_severity(reading)
        telemetry_type = self.sensor_reading_service.determine_telemetry_type(reading)

        # Send to SafeCar backend
        backend_success = self.backend_service.send_telemetry_sample(
            reading=saved_reading,
            telemetry_type=telemetry_type,
            severity=severity
        )

        return {
            'id': saved_reading.id,
            'device_id': saved_reading.device_id,
            'sensor_location': saved_reading.sensor_location,
            'timestamp': saved_reading.timestamp.isoformat() + 'Z',
            'severity': severity,
            'telemetry_type': telemetry_type,
            'backend_synced': backend_success,
            'created_at': saved_reading.created_at.isoformat() + 'Z'
        }

    def get_reading_by_id(self, reading_id: int) -> Optional[Dict[str, Any]]:
        """Get a sensor reading by ID.

        Args:
            reading_id: Reading identifier.

        Returns:
            Optional[Dict]: Reading data if found.
        """
        reading = self.sensor_reading_repository.find_by_id(reading_id)
        if not reading:
            return None

        return self._reading_to_dict(reading)

    def get_vehicle_readings(
        self,
        vehicle_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get sensor readings for a vehicle.

        Args:
            vehicle_id: Vehicle identifier.
            start_date: Start date filter (ISO format).
            end_date: End date filter (ISO format).
            limit: Maximum number of results.

        Returns:
            List[Dict]: List of sensor readings.
        """
        start_dt = None
        end_dt = None

        if start_date:
            start_dt = parse(start_date).astimezone(timezone.utc)

        if end_date:
            end_dt = parse(end_date).astimezone(timezone.utc)

        readings = self.sensor_reading_repository.find_by_vehicle(
            vehicle_id=vehicle_id,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit
        )

        return [self._reading_to_dict(r) for r in readings]

    def get_device_statistics(self, device_id: str, api_key: str) -> Dict[str, Any]:
        """Get statistics for a device.

        Args:
            device_id: Device identifier.
            api_key: API key for authentication.

        Returns:
            Dict: Device statistics.

        Raises:
            ValueError: If authentication fails.
        """
        # Authenticate device
        device = self.iam_service.get_device_by_id_and_api_key(device_id, api_key)
        if not device:
            raise ValueError("Device not found or invalid API key")

        # Get recent readings
        recent_readings = self.sensor_reading_repository.find_recent_by_device(
            device_id=device_id,
            limit=100
        )

        if not recent_readings:
            return {
                'device_id': device_id,
                'total_readings': 0,
                'latest_reading': None
            }

        # Calculate statistics
        latest = recent_readings[0]

        cabin_temp_readings = [r.cabin_temperature_celsius for r in recent_readings if r.has_cabin_temperature_reading()]
        engine_temp_readings = [r.engine_temperature_celsius for r in recent_readings if r.has_engine_temperature_reading()]
        cabin_humidity_readings = [r.cabin_humidity_percent for r in recent_readings if r.has_cabin_humidity_reading()]
        engine_humidity_readings = [r.engine_humidity_percent for r in recent_readings if r.has_engine_humidity_reading()]
        gas_readings = [r.gas_concentration_ppm for r in recent_readings if r.has_gas_reading()]
        current_readings = [r.current_amperes for r in recent_readings if r.has_current_reading()]

        stats = {
            'device_id': device_id,
            'total_readings': len(recent_readings),
            'latest_reading': self._reading_to_dict(latest),
            'cabin_temperature_stats': self._calculate_stats(cabin_temp_readings) if cabin_temp_readings else None,
            'engine_temperature_stats': self._calculate_stats(engine_temp_readings) if engine_temp_readings else None,
            'cabin_humidity_stats': self._calculate_stats(cabin_humidity_readings) if cabin_humidity_readings else None,
            'engine_humidity_stats': self._calculate_stats(engine_humidity_readings) if engine_humidity_readings else None,
            'gas_stats': self._calculate_stats(gas_readings) if gas_readings else None,
            'current_stats': self._calculate_stats(current_readings) if current_readings else None
        }

        return stats

    @staticmethod
    def _reading_to_dict(reading: SensorReading) -> Dict[str, Any]:
        """Convert a SensorReading entity to a dictionary."""
        # Handle both datetime objects and strings
        timestamp_str = reading.timestamp.isoformat() + 'Z' if isinstance(reading.timestamp, datetime) else str(reading.timestamp)
        created_at_str = reading.created_at.isoformat() + 'Z' if isinstance(reading.created_at, datetime) else str(reading.created_at)

        return {
            'id': reading.id,
            'device_id': reading.device_id,
            'sensor_location': reading.sensor_location,
            'cabin_temperature_celsius': reading.cabin_temperature_celsius,
            'cabin_humidity_percent': reading.cabin_humidity_percent,
            'engine_temperature_celsius': reading.engine_temperature_celsius,
            'engine_humidity_percent': reading.engine_humidity_percent,
            'gas_type': reading.gas_type,
            'gas_concentration_ppm': reading.gas_concentration_ppm,
            'latitude': reading.latitude,
            'longitude': reading.longitude,
            'current_amperes': reading.current_amperes,
            'timestamp': timestamp_str,
            'created_at': created_at_str
        }

    @staticmethod
    def _calculate_stats(values: List[float]) -> Dict[str, float]:
        """Calculate basic statistics for a list of values."""
        if not values:
            return {}

        return {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'count': len(values)
        }
