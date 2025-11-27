"""Infrastructure models for Telemetry context using Peewee ORM."""
from peewee import (
    AutoField, CharField, FloatField, IntegerField,
    DateTimeField, Model
)
from shared.infrastructure.database import db


class SensorReading(Model):
    """Peewee model for SensorReading persistence.

    Stores sensor data from two ESP32 devices:
    - ESP32 (CABINA): DHT11, MQ2, NEO6M GPS
    - ESP32 (MOTOR): DHT11, ACS712

    Attributes:
        id (AutoField): Primary key.
        device_id (CharField): Edge device identifier.
        vehicle_id (IntegerField): Vehicle identifier.
        driver_id (IntegerField): Driver identifier.
        sensor_location (CharField): Sensor location ('CABINA' or 'MOTOR').
        cabin_temperature_celsius (FloatField): CABINA DHT11 temperature.
        cabin_humidity_percent (FloatField): CABINA DHT11 humidity.
        engine_temperature_celsius (FloatField): MOTOR DHT11 temperature.
        engine_humidity_percent (FloatField): MOTOR DHT11 humidity.
        gas_type (CharField): MQ2 gas type (CABINA).
        gas_concentration_ppm (FloatField): MQ2 gas concentration (CABINA).
        latitude (FloatField): NEO6M GPS latitude (CABINA).
        longitude (FloatField): NEO6M GPS longitude (CABINA).
        current_amperes (FloatField): ACS712 current (MOTOR).
        timestamp (DateTimeField): When reading was taken.
        created_at (DateTimeField): When record was created.
    """

    id = AutoField(primary_key=True)
    device_id = CharField(max_length=100, index=True)
    vehicle_id = IntegerField(index=True)
    driver_id = IntegerField(index=True)
    sensor_location = CharField(max_length=20, null=True)
    
    # DHT11 sensors (CABINA)
    cabin_temperature_celsius = FloatField(null=True)
    cabin_humidity_percent = FloatField(null=True)
    
    # DHT11 sensors (MOTOR)
    engine_temperature_celsius = FloatField(null=True)
    engine_humidity_percent = FloatField(null=True)
    
    # MQ2 gas sensor (CABINA)
    gas_type = CharField(max_length=50, null=True)
    gas_concentration_ppm = FloatField(null=True)
    
    # NEO6M GPS (CABINA)
    latitude = FloatField(null=True)
    longitude = FloatField(null=True)
    
    # ACS712 current sensor (MOTOR)
    current_amperes = FloatField(null=True)
    
    timestamp = DateTimeField(index=True)
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'sensor_readings'
        indexes = (
            (('vehicle_id', 'timestamp'), False),  # Composite index for queries
            (('device_id', 'timestamp'), False),
        )
