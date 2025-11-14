"""External service integrations for Telemetry context"""
import os
import json
import requests
from typing import Optional, Dict, Any
from telemetry.domain.entities import SensorReading


class SafeCarBackendService:
    """
    Service for integrating with SafeCar backend platform.
    Sends telemetry samples to the backend for processing.
    """
    
    def __init__(self):
        """Initialize the SafeCar backend service with configuration."""
        self.backend_url = os.getenv('SAFECAR_BACKEND_URL', 'http://localhost:8080')
        self.api_key = os.getenv('SAFECAR_BACKEND_API_KEY', '')
        self.telemetry_endpoint = f"{self.backend_url}/api/v1/telemetry"
        self.timeout = 10  # seconds
    
    def send_telemetry_sample(
        self, 
        reading: SensorReading,
        telemetry_type: str,
        severity: str
    ) -> bool:
        """
        Send a telemetry sample to the SafeCar backend.
        
        Args:
            reading: Sensor reading to send
            telemetry_type: Type of telemetry (e.g., CABIN_GAS_DETECTED)
            severity: Alert severity (INFO, WARNING, CRITICAL)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            payload = self._build_telemetry_payload(reading, telemetry_type, severity)
            
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': self.api_key
            }
            
            response = requests.post(
                self.telemetry_endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                return True
            else:
                print(f"Failed to send telemetry: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"Error sending telemetry to backend: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error sending telemetry: {str(e)}")
            return False
    
    def _build_telemetry_payload(
        self, 
        reading: SensorReading,
        telemetry_type: str,
        severity: str
    ) -> Dict[str, Any]:
        """
        Build the telemetry payload compatible with SafeCar backend.
        
        Args:
            reading: Sensor reading
            telemetry_type: Telemetry type
            severity: Alert severity
            
        Returns:
            Dict: Telemetry payload
        """
        # Build the TelemetrySample structure
        sample = {
            "type": telemetry_type,
            "severity": severity,
            "timestamp": {
                "occurredAt": reading.timestamp.isoformat()
            },
            "vehicleId": {
                "vehicleId": reading.vehicle_id
            },
            "driverId": {
                "driverId": reading.driver_id
            }
        }
        
        # Add gas detection data if available
        if reading.has_gas_reading():
            sample["cabinGasLevel"] = {
                "type": reading.gas_type,
                "concentrationPpm": reading.gas_concentration_ppm
            }
        
        # Note: Temperature and Current sensors would require backend extension
        # For now, we can send them as part of gas detection context or create
        # custom telemetry types
        
        # Wrap in IngestTelemetrySampleCommand structure
        payload = {
            "sample": sample
        }
        
        return payload
    
    def test_connection(self) -> bool:
        """
        Test connection to SafeCar backend.
        
        Returns:
            bool: True if backend is reachable
        """
        try:
            response = requests.get(
                f"{self.backend_url}/actuator/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
