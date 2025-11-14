"""Domain entities for the Telemetry bounded context"""
from datetime import datetime, timezone
from typing import Optional


class SensorReading:
    """
    Represents a sensor reading entity in the Telemetry context.
    
    Attributes:
        id (int): Unique identifier for the sensor reading
        device_id (str): Identifier for the device that recorded the reading
        vehicle_id (int): Identifier for the vehicle
        driver_id (int): Identifier for the driver
        temperature_celsius (float): Temperature reading from LM35 sensor
        gas_type (str): Type of gas detected by MQ2 sensor
        gas_concentration_ppm (float): Gas concentration in parts per million
        current_amperes (float): Current reading from ACS712 sensor
        timestamp (datetime): When the reading was taken
        created_at (datetime): When the record was created in the database
    """
    
    def __init__(
        self,
        device_id: str,
        vehicle_id: int,
        driver_id: int,
        temperature_celsius: Optional[float] = None,
        gas_type: Optional[str] = None,
        gas_concentration_ppm: Optional[float] = None,
        current_amperes: Optional[float] = None,
        timestamp: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        id: Optional[int] = None
    ):
        """
        Initialize a SensorReading instance.
        
        Args:
            device_id: Identifier for the device
            vehicle_id: Identifier for the vehicle
            driver_id: Identifier for the driver
            temperature_celsius: Temperature reading (optional)
            gas_type: Type of gas detected (optional)
            gas_concentration_ppm: Gas concentration (optional)
            current_amperes: Current reading (optional)
            timestamp: When the reading was taken (optional, defaults to now)
            created_at: When the record was created (optional, defaults to now)
            id: Unique identifier (optional)
        """
        self.id = id
        self.device_id = device_id
        self.vehicle_id = vehicle_id
        self.driver_id = driver_id
        self.temperature_celsius = temperature_celsius
        self.gas_type = gas_type
        self.gas_concentration_ppm = gas_concentration_ppm
        self.current_amperes = current_amperes
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.created_at = created_at or datetime.now(timezone.utc)
    
    def has_temperature_reading(self) -> bool:
        """Check if temperature reading is available."""
        return self.temperature_celsius is not None
    
    def has_gas_reading(self) -> bool:
        """Check if gas reading is available."""
        return self.gas_type is not None and self.gas_concentration_ppm is not None
    
    def has_current_reading(self) -> bool:
        """Check if current reading is available."""
        return self.current_amperes is not None
    
    def is_valid(self) -> bool:
        """Check if the reading has at least one sensor value."""
        return (
            self.has_temperature_reading() or 
            self.has_gas_reading() or 
            self.has_current_reading()
        )
