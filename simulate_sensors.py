"""Example script for simulating sensor readings from IoT devices.

This script simulates data from two ESP32 devices:

ESP32 (CABINA):
- DHT11: Temperature and Humidity Sensor
- MQ2: Gas Sensor (GLP, butane, propano, metano, alcohol, hidrógeno)
- NEO6M: GPS Module with EEPROM and Reception Antenna

ESP32 (MOTOR):
- DHT11: Temperature and Humidity Sensor
- ACS712-05: Current Sensor (Hall effect, 0-5 Amperes)

Usage:
    python simulate_sensors.py
"""
import os
import time
import random
import requests
from datetime import datetime, timezone


class SensorSimulator:
    """Simulates sensor readings for testing the edge service."""

    def __init__(self, edge_service_url='http://localhost:5000'):
        """Initialize the sensor simulator.

        Args:
            edge_service_url: URL of the edge service.
        """
        self.edge_service_url = edge_service_url
        self.device_id = os.getenv('DEVICE_ID', 'safecar-001')
        self.api_key = os.getenv('API_KEY', 'test-api-key-12345')

        # Simulated location (Lima, Peru)
        self.base_latitude = -12.0464
        self.base_longitude = -77.0428

    def simulate_dht11_cabin(self) -> tuple:
        """Simulate DHT11 sensor reading from CABINA ESP32.

        Normal cabin range: 15°C to 35°C, 30% to 80% humidity

        Returns:
            tuple: (temperature_celsius, humidity_percent)
        """
        # Normal cabin conditions
        if random.random() < 0.1:  # 10% chance of extreme temperature
            temperature = random.uniform(38.0, 45.0)
        else:
            temperature = random.uniform(18.0, 32.0)

        # Humidity
        if random.random() < 0.1:  # 10% chance of high humidity
            humidity = random.uniform(85.0, 95.0)
        else:
            humidity = random.uniform(35.0, 75.0)

        return round(temperature, 1), round(humidity, 1)

    def simulate_dht11_motor(self) -> tuple:
        """Simulate DHT11 sensor reading from MOTOR ESP32.

        Engine compartment: 40°C to 100°C, 20% to 60% humidity

        Returns:
            tuple: (temperature_celsius, humidity_percent)
        """
        # Normal engine temperature
        if random.random() < 0.1:  # 10% chance of overheating
            temperature = random.uniform(105.0, 118.0)
        else:
            temperature = random.uniform(60.0, 98.0)

        # Engine compartment humidity (lower than cabin)
        humidity = random.uniform(25.0, 55.0)

        return round(temperature, 1), round(humidity, 1)

    def simulate_mq2_gas(self) -> tuple:
        """Simulate MQ2 gas sensor reading from CABINA ESP32.

        Returns:
            tuple: (gas_type, concentration_ppm)
        """
        gas_types = ['methane', 'propane', 'butane', 'alcohol', 'hydrogen', 'lpg']

        # Normal: low concentrations
        # Occasional spikes to test alerts
        if random.random() < 0.05:  # 5% chance of gas detection
            gas_type = random.choice(gas_types)
            concentration = random.uniform(1000.0, 6000.0)
            return gas_type, round(concentration, 2)
        else:
            # Baseline ambient levels
            return random.choice(gas_types), round(random.uniform(50.0, 300.0), 2)

    def simulate_neo6m_gps(self) -> tuple:
        """Simulate NEO6M GPS sensor reading from CABINA ESP32.

        Simulates movement around base location (Lima, Peru)

        Returns:
            tuple: (latitude, longitude)
        """
        # Add small random offset to simulate vehicle movement
        lat_offset = random.uniform(-0.01, 0.01)  # ~1km variation
        lon_offset = random.uniform(-0.01, 0.01)

        latitude = round(self.base_latitude + lat_offset, 6)
        longitude = round(self.base_longitude + lon_offset, 6)

        return latitude, longitude

    def simulate_acs712_current(self) -> float:
        """Simulate ACS712-05 current sensor reading from MOTOR ESP32.

        Range: 0-5 Amperes

        Returns:
            float: Current in Amperes
        """
        # Normal operation: 1.5-3.5A
        # Occasional high/low to test alerts
        rand = random.random()
        if rand < 0.05:  # 5% chance of high current
            return round(random.uniform(4.2, 4.9), 3)
        elif rand < 0.1:  # 5% chance of low current (battery issue)
            return round(random.uniform(0.1, 0.4), 3)
        else:
            return round(random.uniform(1.8, 3.2), 3)

    def send_cabina_reading(self) -> bool:
        """Generate and send a sensor reading from ESP32 (CABINA).

        Returns:
            bool: True if successful
        """
        # Simulate CABINA sensors: DHT11, MQ2, NEO6M GPS
        cabin_temp, cabin_humidity = self.simulate_dht11_cabin()
        gas_type, gas_ppm = self.simulate_mq2_gas()
        latitude, longitude = self.simulate_neo6m_gps()

        payload = {
            'sensor_location': 'CABINA',
            'cabin_temperature_celsius': cabin_temp,
            'cabin_humidity_percent': cabin_humidity,
            'gas_type': gas_type,
            'gas_concentration_ppm': gas_ppm,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        headers = {
            'Content-Type': 'application/json',
            'X-Device-Id': self.device_id,
            'X-API-Key': self.api_key
        }

        try:
            response = requests.post(
                f'{self.edge_service_url}/api/v1/telemetry/data-records',
                json=payload,
                headers=headers,
                timeout=5
            )

            if response.status_code == 201:
                result = response.json()
                print(f"✓ CABINA Reading sent successfully:")
                print(f"  ID: {result['data']['id']}")
                print(f"  Cabin Temp: {cabin_temp}°C, Humidity: {cabin_humidity}%")
                print(f"  Gas: {gas_type} @ {gas_ppm:.2f} ppm")
                print(f"  GPS: ({latitude}, {longitude})")
                print(f"  Severity: {result['data']['severity']}")
                print(f"  Backend synced: {result['data']['backend_synced']}")
                return True
            else:
                print(f"✗ Failed to send CABINA reading: HTTP {response.status_code}")
                print(f"  Response: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Error sending CABINA reading: {str(e)}")
            return False

    def send_motor_reading(self) -> bool:
        """Generate and send a sensor reading from ESP32 (MOTOR).

        Returns:
            bool: True if successful
        """
        # Simulate MOTOR sensors: DHT11, ACS712
        engine_temp, engine_humidity = self.simulate_dht11_motor()
        current = self.simulate_acs712_current()

        payload = {
            'sensor_location': 'MOTOR',
            'engine_temperature_celsius': engine_temp,
            'engine_humidity_percent': engine_humidity,
            'current_amperes': current,
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        headers = {
            'Content-Type': 'application/json',
            'X-Device-Id': self.device_id,
            'X-API-Key': self.api_key
        }

        try:
            response = requests.post(
                f'{self.edge_service_url}/api/v1/telemetry/data-records',
                json=payload,
                headers=headers,
                timeout=5
            )

            if response.status_code == 201:
                result = response.json()
                print(f"✓ MOTOR Reading sent successfully:")
                print(f"  ID: {result['data']['id']}")
                print(f"  Engine Temp: {engine_temp}°C, Humidity: {engine_humidity}%")
                print(f"  Current: {current:.3f}A")
                print(f"  Severity: {result['data']['severity']}")
                print(f"  Backend synced: {result['data']['backend_synced']}")
                return True
            else:
                print(f"✗ Failed to send MOTOR reading: HTTP {response.status_code}")
                print(f"  Response: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Error sending MOTOR reading: {str(e)}")
            return False

    def run_continuous(self, interval_seconds=5):
        """Run continuous simulation alternating between CABINA and MOTOR.

        Args:
            interval_seconds: Delay between readings
        """
        print(f"Starting sensor simulation for ESP32 devices...")
        print(f"Edge Service: {self.edge_service_url}")
        print(f"Device ID: {self.device_id}")
        print(f"Interval: {interval_seconds}s")
        print("-" * 60)

        count = 0
        try:
            while True:
                count += 1
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                print(f"\nReading #{count} - {timestamp}")

                # Alternate between CABINA and MOTOR readings
                if count % 2 == 1:
                    self.send_cabina_reading()
                else:
                    self.send_motor_reading()

                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print(f"\n\nSimulation stopped. Total readings sent: {count}")


if __name__ == '__main__':
    simulator = SensorSimulator()
    simulator.run_continuous(interval_seconds=5)
