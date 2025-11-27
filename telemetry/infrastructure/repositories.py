"""Repository implementations for Telemetry context."""
from typing import List, Optional
from datetime import datetime
from telemetry.domain.entities import SensorReading as SensorReadingEntity
from telemetry.infrastructure.models import SensorReading as SensorReadingModel


class SensorReadingRepository:
    """Repository for managing sensor reading persistence.
    
    Handles conversion between domain entities and Peewee ORM models
    for sensor data from ESP32 devices (CABINA and MOTOR).
    """

    def save(self, reading: SensorReadingEntity) -> SensorReadingEntity:
        """Save a sensor reading to the database.

        Args:
            reading (SensorReadingEntity): Sensor reading entity to save.

        Returns:
            SensorReadingEntity: Saved sensor reading entity with ID.
        """
        reading_model = SensorReadingModel.create(
            device_id=reading.device_id,
            vehicle_id=reading.vehicle_id,
            driver_id=reading.driver_id,
            sensor_location=reading.sensor_location,
            cabin_temperature_celsius=reading.cabin_temperature_celsius,
            cabin_humidity_percent=reading.cabin_humidity_percent,
            engine_temperature_celsius=reading.engine_temperature_celsius,
            engine_humidity_percent=reading.engine_humidity_percent,
            gas_type=reading.gas_type,
            gas_concentration_ppm=reading.gas_concentration_ppm,
            latitude=reading.latitude,
            longitude=reading.longitude,
            current_amperes=reading.current_amperes,
            timestamp=reading.timestamp,
            created_at=reading.created_at
        )

        return self._to_entity(reading_model)

    def find_by_id(self, reading_id: int) -> Optional[SensorReadingEntity]:
        """Find a sensor reading by its ID.

        Args:
            reading_id (int): Reading identifier.

        Returns:
            Optional[SensorReadingEntity]: Reading entity if found, None otherwise.
        """
        try:
            reading_model = SensorReadingModel.get_by_id(reading_id)
            return self._to_entity(reading_model)
        except SensorReadingModel.DoesNotExist:
            return None

    def find_by_vehicle(
        self,
        vehicle_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SensorReadingEntity]:
        """Find sensor readings by vehicle ID with optional date range.

        Args:
            vehicle_id: Vehicle identifier.
            start_date: Start date filter (optional).
            end_date: End date filter (optional).
            limit: Maximum number of results.

        Returns:
            List[SensorReadingEntity]: List of sensor readings.
        """
        query = SensorReadingModel.select().where(
            SensorReadingModel.vehicle_id == vehicle_id
        )

        if start_date:
            query = query.where(SensorReadingModel.timestamp >= start_date)

        if end_date:
            query = query.where(SensorReadingModel.timestamp <= end_date)

        query = query.order_by(SensorReadingModel.timestamp.desc()).limit(limit)

        return [self._to_entity(model) for model in query]

    def find_recent_by_device(
        self,
        device_id: str,
        limit: int = 50
    ) -> List[SensorReadingEntity]:
        """Find recent sensor readings by device ID.

        Args:
            device_id: Device identifier.
            limit: Maximum number of results.

        Returns:
            List[SensorReadingEntity]: List of recent sensor readings.
        """
        query = SensorReadingModel.select().where(
            SensorReadingModel.device_id == device_id
        ).order_by(SensorReadingModel.timestamp.desc()).limit(limit)

        return [self._to_entity(model) for model in query]

    def count_by_vehicle(self, vehicle_id: int) -> int:
        """Count sensor readings for a vehicle.

        Args:
            vehicle_id: Vehicle identifier.

        Returns:
            int: Number of readings.
        """
        return SensorReadingModel.select().where(
            SensorReadingModel.vehicle_id == vehicle_id
        ).count()

    @staticmethod
    def _to_entity(model: SensorReadingModel) -> SensorReadingEntity:
        """Convert a Peewee model to a domain entity.

        Args:
            model (SensorReadingModel): Peewee model instance.

        Returns:
            SensorReadingEntity: Domain entity.
        """
        return SensorReadingEntity(
            id=model.id,
            device_id=model.device_id,
            vehicle_id=model.vehicle_id,
            driver_id=model.driver_id,
            sensor_location=model.sensor_location,
            cabin_temperature_celsius=model.cabin_temperature_celsius,
            cabin_humidity_percent=model.cabin_humidity_percent,
            engine_temperature_celsius=model.engine_temperature_celsius,
            engine_humidity_percent=model.engine_humidity_percent,
            gas_type=model.gas_type,
            gas_concentration_ppm=model.gas_concentration_ppm,
            latitude=model.latitude,
            longitude=model.longitude,
            current_amperes=model.current_amperes,
            timestamp=model.timestamp,
            created_at=model.created_at
        )
