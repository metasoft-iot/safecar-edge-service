"""Domain services for Telemetry context"""
from datetime import datetime, timezone
from typing import Optional

from dateutil.parser import parse

from telemetry.domain.entities import SensorReading


class SensorReadingService:
    """
    Domain service for managing sensor reading business logic.
    """
    
    def __init__(self):
        """
        Initialize the SensorReadingService.
        """
        pass
    
    # Temperature thresholds (Celsius)
    TEMP_CRITICAL_HIGH = 110.0  # Engine critical temperature
    TEMP_WARNING_HIGH = 95.0    # Engine warning temperature
    TEMP_WARNING_LOW = -10.0    # Cabin warning temperature
    
    # Gas concentration thresholds (PPM)
    GAS_CRITICAL_PPM = 5000.0   # Critical gas level
    GAS_WARNING_PPM = 1000.0    # Warning gas level
    
    # Current thresholds (Amperes)
    CURRENT_CRITICAL_HIGH = 4.5  # Near max capacity
    CURRENT_WARNING_HIGH = 4.0   # High current warning
    CURRENT_WARNING_LOW = 0.5    # Low current warning (possible battery drain)
    
    @staticmethod
    def create_sensor_reading(
        device_id: str,
        vehicle_id: int,
        driver_id: int,
        temperature_celsius: Optional[float] = None,
        gas_type: Optional[str] = None,
        gas_concentration_ppm: Optional[float] = None,
        current_amperes: Optional[float] = None,
        timestamp: Optional[str] = None
    ) -> SensorReading:
        """
        Create a new sensor reading with validation.
        
        Args:
            device_id: Device identifier
            vehicle_id: Vehicle identifier
            driver_id: Driver identifier
            temperature_celsius: Temperature reading
            gas_type: Type of gas detected
            gas_concentration_ppm: Gas concentration
            current_amperes: Current reading
            timestamp: ISO format timestamp
            
        Returns:
            SensorReading: New sensor reading instance
            
        Raises:
            ValueError: If validation fails
        """
        if not device_id or not device_id.strip():
            raise ValueError("Device ID cannot be empty")
        
        if vehicle_id is None or vehicle_id <= 0:
            raise ValueError("Vehicle ID must be a positive integer")
        
        if driver_id is None or driver_id <= 0:
            raise ValueError("Driver ID must be a positive integer")
        
        # Validate temperature range (-55°C to +150°C for LM35)
        if temperature_celsius is not None:
            if temperature_celsius < -55.0 or temperature_celsius > 150.0:
                raise ValueError("Temperature must be between -55°C and 150°C")
        
        # Validate gas concentration
        if gas_concentration_ppm is not None:
            if gas_concentration_ppm < 0:
                raise ValueError("Gas concentration cannot be negative")
            if gas_type is None or not gas_type.strip():
                raise ValueError("Gas type is required when concentration is provided")
        
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
            temperature_celsius=temperature_celsius,
            gas_type=gas_type.strip() if gas_type else None,
            gas_concentration_ppm=gas_concentration_ppm,
            current_amperes=current_amperes,
            timestamp=timestamp_dt
        )
        
        if not reading.is_valid():
            raise ValueError("At least one sensor reading must be provided")
        
        return reading
    
    @staticmethod
    def determine_alert_severity(reading: SensorReading) -> str:
        """
        Determine the alert severity level based on sensor readings.
        
        Args:
            reading: Sensor reading to evaluate
            
        Returns:
            str: Alert severity level (INFO, WARNING, CRITICAL)
        """
        severity = "INFO"
        
        # Check temperature
        if reading.has_temperature_reading():
            temp = reading.temperature_celsius
            if temp >= SensorReadingService.TEMP_CRITICAL_HIGH or temp <= SensorReadingService.TEMP_WARNING_LOW:
                severity = "CRITICAL"
            elif temp >= SensorReadingService.TEMP_WARNING_HIGH:
                severity = "WARNING"
        
        # Check gas concentration
        if reading.has_gas_reading():
            gas_ppm = reading.gas_concentration_ppm
            if gas_ppm >= SensorReadingService.GAS_CRITICAL_PPM:
                severity = "CRITICAL"
            elif gas_ppm >= SensorReadingService.GAS_WARNING_PPM and severity == "INFO":
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
        """
        Determine the primary telemetry type based on readings.
        
        Args:
            reading: Sensor reading to evaluate
            
        Returns:
            str: Telemetry type
        """
        # Prioritize critical conditions
        severity = SensorReadingService.determine_alert_severity(reading)
        
        if severity == "CRITICAL":
            if reading.has_gas_reading():
                return "CABIN_GAS_DETECTED"
            if reading.has_temperature_reading():
                return "ENGINE_OVERHEAT"
            if reading.has_current_reading():
                return "ELECTRICAL_FAULT"
        
        # Default types based on available sensors
        if reading.has_gas_reading():
            return "CABIN_GAS_DETECTED"
        if reading.has_temperature_reading():
            return "TEMPERATURE"
        if reading.has_current_reading():
            return "ELECTRICAL_FAULT"
        
        return "GENERAL"
