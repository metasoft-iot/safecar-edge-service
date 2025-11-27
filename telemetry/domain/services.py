"""Domain services for Telemetry context."""
from datetime import datetime, timezone
from typing import Optional

from dateutil.parser import parse

from telemetry.domain.entities import SensorReading


class SensorReadingService:
    """Domain service for managing sensor reading business logic.
    
    Handles validation, severity determination, and telemetry type classification
    for sensor data from two ESP32 devices (CABINA and MOTOR).
    """

    def __init__(self):
        """Initialize the SensorReadingService."""
        pass

    # Temperature thresholds (Celsius) for DHT11 sensors
    CABIN_TEMP_CRITICAL_HIGH = 50.0    # Critical cabin temperature
    CABIN_TEMP_WARNING_HIGH = 40.0     # Warning cabin temperature
    ENGINE_TEMP_CRITICAL_HIGH = 110.0  # Critical engine temperature
    ENGINE_TEMP_WARNING_HIGH = 95.0    # Warning engine temperature
    TEMP_WARNING_LOW = -10.0           # Warning low temperature

    # Humidity thresholds (%) for DHT11 sensors
    HUMIDITY_CRITICAL_HIGH = 90.0  # Very high humidity
    HUMIDITY_WARNING_HIGH = 75.0   # High humidity
    HUMIDITY_WARNING_LOW = 20.0    # Low humidity (dry air)

    # Gas concentration thresholds (PPM) for MQ2 sensor
    GAS_CRITICAL_PPM = 5000.0   # Critical gas level
    GAS_WARNING_PPM = 1000.0    # Warning gas level

    # Current thresholds (Amperes) for ACS712 sensor
    CURRENT_CRITICAL_HIGH = 4.5  # Near max capacity
    CURRENT_WARNING_HIGH = 4.0   # High current warning
    CURRENT_WARNING_LOW = 0.5    # Low current warning (possible battery drain)

    @staticmethod
    def create_sensor_reading(
        device_id: str,
        vehicle_id: int,
        driver_id: int,
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
    ) -> SensorReading:
        """Create a new sensor reading with validation.

        Args:
            device_id: Device identifier.
            vehicle_id: Vehicle identifier.
            driver_id: Driver identifier.
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
            SensorReading: New sensor reading instance.

        Raises:
            ValueError: If validation fails.
        """
        if not device_id or not device_id.strip():
            raise ValueError("Device ID cannot be empty")

        if vehicle_id is None or vehicle_id <= 0:
            raise ValueError("Vehicle ID must be a positive integer")

        if driver_id is None or driver_id <= 0:
            raise ValueError("Driver ID must be a positive integer")

        # Validate sensor_location
        if sensor_location and sensor_location not in ['CABINA', 'MOTOR']:
            raise ValueError("Sensor location must be 'CABINA' or 'MOTOR'")

        # Validate cabin temperature range (-40°C to +80°C for DHT11)
        if cabin_temperature_celsius is not None:
            if cabin_temperature_celsius < -40.0 or cabin_temperature_celsius > 80.0:
                raise ValueError("Cabin temperature must be between -40°C and 80°C")

        # Validate engine temperature range (-40°C to +125°C)
        if engine_temperature_celsius is not None:
            if engine_temperature_celsius < -40.0 or engine_temperature_celsius > 125.0:
                raise ValueError("Engine temperature must be between -40°C and 125°C")

        # Validate humidity range (0% to 100% for DHT11)
        if cabin_humidity_percent is not None:
            if cabin_humidity_percent < 0.0 or cabin_humidity_percent > 100.0:
                raise ValueError("Cabin humidity must be between 0% and 100%")

        if engine_humidity_percent is not None:
            if engine_humidity_percent < 0.0 or engine_humidity_percent > 100.0:
                raise ValueError("Engine humidity must be between 0% and 100%")

        # Validate gas concentration
        if gas_concentration_ppm is not None:
            if gas_concentration_ppm < 0:
                raise ValueError("Gas concentration cannot be negative")
            if gas_type is None or not gas_type.strip():
                raise ValueError("Gas type is required when concentration is provided")

        # Validate GPS coordinates
        if latitude is not None:
            if latitude < -90.0 or latitude > 90.0:
                raise ValueError("Latitude must be between -90 and 90 degrees")

        if longitude is not None:
            if longitude < -180.0 or longitude > 180.0:
                raise ValueError("Longitude must be between -180 and 180 degrees")

        # GPS coordinates should be provided together
        if (latitude is not None and longitude is None) or (latitude is None and longitude is not None):
            raise ValueError("Latitude and longitude must be provided together")

        # Validate current (0-5A for ACS712-05)
        if current_amperes is not None:
            if current_amperes < 0 or current_amperes > 5.0:
                raise ValueError("Current must be between 0 and 5 Amperes")

        # Parse timestamp if provided
        timestamp_dt = None
        if timestamp:
            try:
                timestamp_dt = parse(timestamp).astimezone(timezone.utc)
            except (ValueError, TypeError):
                raise ValueError("Invalid timestamp format. Use ISO 8601 format")

        reading = SensorReading(
            device_id=device_id.strip(),
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            sensor_location=sensor_location,
            cabin_temperature_celsius=cabin_temperature_celsius,
            cabin_humidity_percent=cabin_humidity_percent,
            engine_temperature_celsius=engine_temperature_celsius,
            engine_humidity_percent=engine_humidity_percent,
            gas_type=gas_type.strip() if gas_type else None,
            gas_concentration_ppm=gas_concentration_ppm,
            latitude=latitude,
            longitude=longitude,
            current_amperes=current_amperes,
            timestamp=timestamp_dt
        )

        if not reading.is_valid():
            raise ValueError("At least one sensor reading must be provided")

        return reading

    @staticmethod
    def determine_alert_severity(reading: SensorReading) -> str:
        """Determine the alert severity level based on sensor readings.

        Args:
            reading: Sensor reading to evaluate.

        Returns:
            str: Alert severity level (INFO, WARNING, CRITICAL).
        """
        severity = "INFO"

        # Check cabin temperature
        if reading.has_cabin_temperature_reading():
            temp = reading.cabin_temperature_celsius
            if temp >= SensorReadingService.CABIN_TEMP_CRITICAL_HIGH or temp <= SensorReadingService.TEMP_WARNING_LOW:
                severity = "CRITICAL"
            elif temp >= SensorReadingService.CABIN_TEMP_WARNING_HIGH:
                severity = "WARNING"

        # Check engine temperature
        if reading.has_engine_temperature_reading():
            temp = reading.engine_temperature_celsius
            if temp >= SensorReadingService.ENGINE_TEMP_CRITICAL_HIGH:
                severity = "CRITICAL"
            elif temp >= SensorReadingService.ENGINE_TEMP_WARNING_HIGH and severity != "CRITICAL":
                severity = "WARNING"

        # Check humidity (cabin or engine)
        for humidity in [reading.cabin_humidity_percent, reading.engine_humidity_percent]:
            if humidity is not None:
                if humidity >= SensorReadingService.HUMIDITY_CRITICAL_HIGH:
                    if severity != "CRITICAL":
                        severity = "WARNING"
                elif humidity <= SensorReadingService.HUMIDITY_WARNING_LOW and severity == "INFO":
                    severity = "WARNING"

        # Check gas concentration
        if reading.has_gas_reading():
            gas_ppm = reading.gas_concentration_ppm
            if gas_ppm >= SensorReadingService.GAS_CRITICAL_PPM:
                severity = "CRITICAL"
            elif gas_ppm >= SensorReadingService.GAS_WARNING_PPM and severity != "CRITICAL":
                severity = "WARNING"

        # Check current
        if reading.has_current_reading():
            current = reading.current_amperes
            if current >= SensorReadingService.CURRENT_CRITICAL_HIGH or current <= SensorReadingService.CURRENT_WARNING_LOW:
                if severity != "CRITICAL":
                    severity = "WARNING"
            elif current >= SensorReadingService.CURRENT_WARNING_HIGH and severity == "INFO":
                severity = "WARNING"

        return severity

    @staticmethod
    def determine_telemetry_type(reading: SensorReading) -> str:
        """Determine the primary telemetry type based on readings.

        Args:
            reading: Sensor reading to evaluate.

        Returns:
            str: Telemetry type compatible with backend TelemetryType enum.
        """
        # Prioritize critical conditions
        severity = SensorReadingService.determine_alert_severity(reading)

        if severity == "CRITICAL":
            if reading.has_gas_reading():
                return "CABIN_GAS_DETECTED"
            if reading.has_engine_temperature_reading():
                return "ENGINE_OVERHEAT"
            if reading.has_current_reading():
                return "ELECTRICAL_FAULT"

        # Default types based on available sensors
        if reading.has_gas_reading():
            return "CABIN_GAS_DETECTED"
        if reading.has_gps_reading():
            return "LOCATION_UPDATE"
        if reading.has_engine_temperature_reading() or reading.has_cabin_temperature_reading():
            return "TEMPERATURE_ANOMALY"
        if reading.has_current_reading():
            return "ELECTRICAL_FAULT"

        return "GENERAL"
