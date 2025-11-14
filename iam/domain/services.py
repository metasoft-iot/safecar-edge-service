"""Domain services for IAM context"""
from datetime import datetime, timezone
from iam.domain.entities import Device


class DeviceService:
    """
    Domain service for managing device business logic.
    """
    
    def __init__(self):
        """
        Initialize the DeviceService.
        """
        pass
    
    @staticmethod
    def create_device(device_id: str, api_key: str) -> Device:
        """
        Create a new device with validation.
        
        Args:
            device_id (str): Unique identifier for the device
            api_key (str): API key for authentication
            
        Returns:
            Device: New device instance
            
        Raises:
            ValueError: If device_id or api_key are invalid
        """
        if not device_id or not device_id.strip():
            raise ValueError("Device ID cannot be empty")
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        if len(api_key) < 8:
            raise ValueError("API key must be at least 8 characters long")
            
        return Device(
            device_id=device_id.strip(),
            api_key=api_key.strip(),
            created_at=datetime.now(timezone.utc)
        )
    
    @staticmethod
    def validate_credentials(device: Device, provided_api_key: str) -> bool:
        """
        Validate device credentials.
        
        Args:
            device (Device): The device to validate
            provided_api_key (str): API key to validate
            
        Returns:
            bool: True if credentials are valid
        """
        if not device or not provided_api_key:
            return False
        return device.api_key == provided_api_key
