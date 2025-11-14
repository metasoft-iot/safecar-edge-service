"""Repository implementations for IAM context"""
from typing import Optional
from iam.domain.entities import Device as DeviceEntity
from iam.infrastructure.models import Device as DeviceModel


class DeviceRepository:
    """
    Repository for managing device persistence.
    """
    
    def save(self, device: DeviceEntity) -> DeviceEntity:
        """
        Save or update a device in the database.
        
        Args:
            device (DeviceEntity): Device entity to save
            
        Returns:
            DeviceEntity: Saved device entity
        """
        device_model, created = DeviceModel.get_or_create(
            device_id=device.device_id,
            defaults={
                'api_key': device.api_key,
                'created_at': device.created_at
            }
        )
        
        if not created:
            device_model.api_key = device.api_key
            device_model.created_at = device.created_at
            device_model.save()
        
        return self._to_entity(device_model)
    
    def find_by_id(self, device_id: str) -> Optional[DeviceEntity]:
        """
        Find a device by its ID.
        
        Args:
            device_id (str): Device identifier
            
        Returns:
            Optional[DeviceEntity]: Device entity if found, None otherwise
        """
        try:
            device_model = DeviceModel.get(DeviceModel.device_id == device_id)
            return self._to_entity(device_model)
        except DeviceModel.DoesNotExist:
            return None
    
    @staticmethod
    def get_or_create_test_device() -> DeviceEntity:
        """
        Get or create a test device for development/testing purposes.
        
        Returns:
            DeviceEntity: Test device entity
        """
        from datetime import datetime, timezone
        device_model, _ = DeviceModel.get_or_create(
            device_id="edge-device-001",
            defaults={
                "api_key": "test-api-key-12345",
                "created_at": datetime.now(timezone.utc)
            }
        )
        return DeviceEntity(
            device_id=device_model.device_id,
            api_key=device_model.api_key,
            created_at=device_model.created_at
        )
    
    def find_by_id_and_api_key(self, device_id: str, api_key: str) -> Optional[DeviceEntity]:
        """
        Find a device by ID and API key (authentication).
        
        Args:
            device_id (str): Device identifier
            api_key (str): API key for authentication
            
        Returns:
            Optional[DeviceEntity]: Device entity if found and authenticated, None otherwise
        """
        try:
            device_model = DeviceModel.get(
                (DeviceModel.device_id == device_id) & 
                (DeviceModel.api_key == api_key)
            )
            return self._to_entity(device_model)
        except DeviceModel.DoesNotExist:
            return None
    
    @staticmethod
    def _to_entity(model: DeviceModel) -> DeviceEntity:
        """
        Convert a Peewee model to a domain entity.
        
        Args:
            model (DeviceModel): Peewee model instance
            
        Returns:
            DeviceEntity: Domain entity
        """
        return DeviceEntity(
            device_id=model.device_id,
            api_key=model.api_key,
            created_at=model.created_at
        )
