"""Application services for IAM context"""
from typing import Optional
from iam.domain.entities import Device
from iam.domain.services import DeviceService
from iam.infrastructure.repositories import DeviceRepository


class AuthApplicationService:
    """
    Application service for authentication and device management.
    """
    
    def __init__(self):
        """
        Initialize the AuthApplicationService with necessary repositories and services.
        """
        self.device_repository = DeviceRepository()
        self.device_service = DeviceService()
    
    def authenticate(self, device_id: str, api_key: str) -> bool:
        """
        Authenticate device using device ID and API key.
        
        Args:
            device_id (str): The ID of the device to authenticate
            api_key (str): The API key of the device to authenticate
            
        Returns:
            bool: True if authentication is successful, False otherwise
        """
        device = self.device_repository.find_by_id_and_api_key(device_id, api_key)
        return device is not None
    
    def register_device(self, device_id: str, api_key: str) -> Device:
        """
        Register a new device.
        
        Args:
            device_id (str): Unique device identifier
            api_key (str): API key for authentication
            
        Returns:
            Device: Registered device
            
        Raises:
            ValueError: If device validation fails
        """
        device = self.device_service.create_device(device_id, api_key)
        return self.device_repository.save(device)
    
    def authenticate_device(self, device_id: str, api_key: str) -> Optional[Device]:
        """
        Authenticate a device using device_id and api_key.
        
        Args:
            device_id (str): Device identifier
            api_key (str): API key to validate
            
        Returns:
            Optional[Device]: Authenticated device if valid, None otherwise
        """
        return self.device_repository.find_by_id_and_api_key(device_id, api_key)
    
    def get_device_by_id(self, device_id: str) -> Optional[Device]:
        """
        Get a device by its ID.
        
        Args:
            device_id (str): Device identifier
            
        Returns:
            Optional[Device]: Device if found, None otherwise
        """
        return self.device_repository.find_by_id(device_id)
    
    def get_device_by_id_and_api_key(self, device_id: str, api_key: str) -> Optional[Device]:
        """
        Get a device by ID and validate API key.
        
        Args:
            device_id (str): Device identifier
            api_key (str): API key to validate
            
        Returns:
            Optional[Device]: Device if found and valid, None otherwise
        """
        return self.device_repository.find_by_id_and_api_key(device_id, api_key)
    
    def get_or_create_test_device(self) -> Device:
        """
        Get or create a test device for development purposes.
        
        Returns:
            Device: Test device
        """
        return self.device_repository.get_or_create_test_device()
