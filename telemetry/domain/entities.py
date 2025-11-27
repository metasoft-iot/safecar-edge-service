"""Domain entities for the Telemetry bounded context."""
from datetime import datetime, timezone
from typing import Optional


class SensorReading:
    """Represents a sensor reading entity in the Telemetry context.

    This entity supports data from two ESP32 devices:
    - ESP32 (CABINA): DHT11, MQ2, NEO6M GPS
    - ESP32 (MOTOR): DHT11, ACS712

    Attributes:
        id (int): Unique identifier for the sensor reading.
        device_id (str): Identifier for the edge device that recorded the reading.
        vehicle_id (int): Identifier for the vehicle.
        driver_id (int): Identifier for the driver.
        sensor_location (str): Location of sensors ('CABINA' or 'MOTOR').
        cabin_temperature_celsius (float): Temperature from CABINA DHT11 sensor.
        cabin_humidity_percent (float): Humidity from CABINA DHT11 sensor.
        engine_temperature_celsius (float): Temperature from MOTOR DHT11 sensor.
        engine_humidity_percent (float): Humidity from MOTOR DHT11 sensor.
        gas_type (str): Type of gas detected by MQ2 sensor (CABINA).
        gas_concentration_ppm (float): Gas concentration in parts per million (CABINA).
        latitude (float): GPS latitude from NEO6M sensor (CABINA).
        longitude (float): GPS longitude from NEO6M sensor (CABINA).
        current_amperes (float): Current reading from ACS712 sensor (MOTOR).
        timestamp (datetime): When the reading was taken.
        created_at (datetime): When the record was created in the database.
    """

    def __init__(
        self,
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
        timestamp: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        id: Optional[int] = None
    ):
        """Initialize a SensorReading instance.

        Args:
            device_id: Identifier for the edge device.
            vehicle_id: Identifier for the vehicle.
            driver_id: Identifier for the driver.
            sensor_location: Location of sensors ('CABINA' or 'MOTOR').
            cabin_temperature_celsius: Temperature from CABINA DHT11 (optional).
            cabin_humidity_percent: Humidity from CABINA DHT11 (optional).
            engine_temperature_celsius: Temperature from MOTOR DHT11 (optional).
            engine_humidity_percent: Humidity from MOTOR DHT11 (optional).
            gas_type: Type of gas detected by MQ2 (optional).
            gas_concentration_ppm: Gas concentration (optional).
            latitude: GPS latitude from NEO6M (optional).
            longitude: GPS longitude from NEO6M (optional).
            current_amperes: Current from ACS712 (optional).
            timestamp: When the reading was taken (optional, defaults to now).
            created_at: When the record was created (optional, defaults to now).
            id: Unique identifier (optional).
        """
        self.id = id
        self.device_id = device_id
        self.vehicle_id = vehicle_id
        self.driver_id = driver_id
        self.sensor_location = sensor_location
        self.cabin_temperature_celsius = cabin_temperature_celsius
        self.cabin_humidity_percent = cabin_humidity_percent
        self.engine_temperature_celsius = engine_temperature_celsius
        self.engine_humidity_percent = engine_humidity_percent
        self.gas_type = gas_type
        self.gas_concentration_ppm = gas_concentration_ppm
        self.latitude = latitude
        self.longitude = longitude
        self.current_amperes = current_amperes
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.created_at = created_at or datetime.now(timezone.utc)

    def has_cabin_temperature_reading(self) -> bool:
        """Check if cabin temperature reading is available."""
        return self.cabin_temperature_celsius is not None

    def has_cabin_humidity_reading(self) -> bool:
        """Check if cabin humidity reading is available."""
        return self.cabin_humidity_percent is not None

    def has_engine_temperature_reading(self) -> bool:
        """Check if engine temperature reading is available."""
        return self.engine_temperature_celsius is not None

    def has_engine_humidity_reading(self) -> bool:
        """Check if engine humidity reading is available."""
        return self.engine_humidity_percent is not None

    def has_gas_reading(self) -> bool:
        """Check if gas reading is available."""
        return self.gas_type is not None and self.gas_concentration_ppm is not None

    def has_gps_reading(self) -> bool:
        """Check if GPS reading is available."""
        return self.latitude is not None and self.longitude is not None

    def has_current_reading(self) -> bool:
        """Check if current reading is available."""
        return self.current_amperes is not None

    def is_valid(self) -> bool:
        """Check if the reading has at least one sensor value."""
        return (
            self.has_cabin_temperature_reading() or
            self.has_cabin_humidity_reading() or
            self.has_engine_temperature_reading() or
            self.has_engine_humidity_reading() or
            self.has_gas_reading() or
            self.has_gps_reading() or
            self.has_current_reading()
        )

    def is_from_cabina(self) -> bool:
        """Check if reading is from CABINA ESP32."""
        return self.sensor_location == 'CABINA'

    def is_from_motor(self) -> bool:
        """Check if reading is from MOTOR ESP32."""
        return self.sensor_location == 'MOTOR'

