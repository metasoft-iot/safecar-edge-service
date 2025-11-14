"""
Example script for simulating sensor readings from IoT devices.

This script simulates data from:
- LM35 Temperature Sensor
- MQ2 Gas Sensor  
- ACS712-05 Current Sensor

Usage:
    python simulate_sensors.py
"""
import time
import random
import requests
import json
from datetime import datetime, timezone


class SensorSimulator:
    """Simulates sensor readings for testing the edge service."""
    
    def __init__(self, edge_service_url='http://localhost:5000'):
        """
        Initialize the sensor simulator.
        
        Args:
            edge_service_url: URL of the edge service
        """
        self.edge_service_url = edge_service_url
        self.device_id = 'edge-device-001'
        self.api_key = 'test-api-key-12345'
    
    def simulate_lm35_temperature(self) -> float:
        """
        Simulate LM35 temperature sensor reading.
        Normal operating range: 20°C to 95°C
        
        Returns:
            float: Temperature in Celsius
        """
        # Normal driving: 20-90°C
        # Occasional spikes to test alerts
        if random.random() < 0.1:  # 10% chance of high temperature
            return random.uniform(95.0, 115.0)
        else:
            return random.uniform(20.0, 90.0)
    
    def simulate_mq2_gas(self) -> tuple:
        """
        Simulate MQ2 gas sensor reading.
        
        Returns:
            tuple: (gas_type, concentration_ppm)
        """
        gas_types = ['methane', 'propane', 'butane', 'alcohol', 'hydrogen', 'lpg']
        
        # Normal: low concentrations
        # Occasional spikes to test alerts
        if random.random() < 0.05:  # 5% chance of gas detection
            gas_type = random.choice(gas_types)
            concentration = random.uniform(500.0, 6000.0)
            return gas_type, concentration
        else:
            # Baseline ambient levels
            return random.choice(gas_types), random.uniform(50.0, 300.0)
    
    def simulate_acs712_current(self) -> float:
        """
        Simulate ACS712-05 current sensor reading.
        Range: 0-5 Amperes
        
        Returns:
            float: Current in Amperes
        """
        # Normal operation: 1-3A
        # Occasional high/low to test alerts
        rand = random.random()
        if rand < 0.05:  # 5% chance of high current
            return random.uniform(4.0, 5.0)
        elif rand < 0.1:  # 5% chance of low current (battery issue)
            return random.uniform(0.0, 0.5)
        else:
            return random.uniform(1.0, 3.0)
    
    def send_reading(self) -> bool:
        """
        Generate and send a sensor reading to the edge service.
        
        Returns:
            bool: True if successful
        """
        # Simulate sensor readings
        temperature = self.simulate_lm35_temperature()
        gas_type, gas_ppm = self.simulate_mq2_gas()
        current = self.simulate_acs712_current()
        
        # Prepare payload
        payload = {
            'device_id': self.device_id,
            'temperature_celsius': round(temperature, 2),
            'gas_type': gas_type,
            'gas_concentration_ppm': round(gas_ppm, 2),
            'current_amperes': round(current, 3),
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-Device-Id': self.device_id,
            'X-API-Key': self.api_key
        }
        
        try:
            response = requests.post(
                f'{self.edge_service_url}/api/v1/telemetry/samples',
                json=payload,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✓ Reading sent successfully:")
                print(f"  ID: {result['data']['id']}")
                print(f"  Temperature: {temperature:.2f}°C")
                print(f"  Gas: {gas_type} @ {gas_ppm:.2f} ppm")
                print(f"  Current: {current:.3f}A")
                print(f"  Severity: {result['data']['severity']}")
                print(f"  Backend synced: {result['data']['backend_synced']}")
                return True
            else:
                print(f"✗ Failed to send reading: HTTP {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Error sending reading: {str(e)}")
            return False
    
    def run_continuous(self, interval_seconds=5):
        """
        Run continuous simulation.
        
        Args:
            interval_seconds: Delay between readings
        """
        print(f"Starting sensor simulation...")
        print(f"Edge Service: {self.edge_service_url}")
        print(f"Device ID: {self.device_id}")
        print(f"Interval: {interval_seconds}s")
        print("-" * 60)
        
        count = 0
        try:
            while True:
                count += 1
                print(f"\nReading #{count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.send_reading()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print(f"\n\nSimulation stopped. Total readings sent: {count}")


if __name__ == '__main__':
    simulator = SensorSimulator()
    simulator.run_continuous(interval_seconds=5)
