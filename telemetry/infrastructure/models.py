"""Infrastructure models for Telemetry context using Peewee ORM"""
from peewee import (
    AutoField, CharField, FloatField, IntegerField, 
    DateTimeField, Model
)
from shared.infrastructure.database import db


class SensorReading(Model):
    """
    Peewee model for SensorReading persistence.
    """
    id = AutoField(primary_key=True)
    device_id = CharField(max_length=100, index=True)
    vehicle_id = IntegerField(index=True)
    driver_id = IntegerField(index=True)
    temperature_celsius = FloatField(null=True)
    gas_type = CharField(max_length=50, null=True)
    gas_concentration_ppm = FloatField(null=True)
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
