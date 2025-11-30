"""Quick test script to verify Edge Service to Backend integration.

This script sends a sample telemetry reading through the full pipeline:
ESP32 → Edge Service → Backend

Make sure both services are running:
1. Backend: ./mvnw spring-boot:run (port 8080)
2. Edge Service: python app.py (port 5000)
"""
import requests
import json
import os
from datetime import datetime, timezone

# Edge Service endpoint
EDGE_SERVICE_URL = os.getenv("EDGE_SERVICE_URL", "http://localhost:5000/api/v1/telemetry/data-records")

# Device credentials (set via env for real devices; test defaults remain for local)
DEVICE_ID = os.getenv("DEVICE_ID", "safecar-001")
API_KEY = os.getenv("API_KEY", "test-api-key-12345")

def test_cabina_data():
    """Test sending CABINA sensor data (DHT11, MQ2, GPS)."""
    print("\n=== Testing CABINA Data ===")
    
    payload = {
        "sensor_location": "CABINA",
        "cabin_temperature_celsius": 28.5,
        "cabin_humidity_percent": 68.0,
        "gas_type": "methane",
        "gas_concentration_ppm": 1250.0,  # Above threshold (> 1000)
        "latitude": -12.0464,
        "longitude": -77.0428,
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Device-Id": DEVICE_ID,
        "X-API-Key": API_KEY
    }
    
    print(f"Sending to: {EDGE_SERVICE_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(EDGE_SERVICE_URL, json=payload, headers=headers, timeout=10)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            data = response.json()
            print("\n✓ CABINA data sent successfully!")
            print(f"  - Reading ID: {data['data']['id']}")
            print(f"  - Severity: {data['data']['severity']}")
            print(f"  - Backend Synced: {data['data']['backend_synced']}")
            print(f"  - Telemetry Type: {data['data']['telemetry_type']}")
            return True
        else:
            print(f"\n✗ Failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection Error!")
        print("Make sure Edge Service is running: python app.py")
        return False
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


def test_motor_data():
    """Test sending MOTOR sensor data (DHT11, ACS712)."""
    print("\n=== Testing MOTOR Data ===")
    
    payload = {
        "sensor_location": "MOTOR",
        "engine_temperature_celsius": 98.5,  # High but not critical
        "current_amperes": 4.3,  # High current (> 4.0A)
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Device-Id": DEVICE_ID,
        "X-API-Key": API_KEY
    }
    
    print(f"Sending to: {EDGE_SERVICE_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(EDGE_SERVICE_URL, json=payload, headers=headers, timeout=10)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            data = response.json()
            print("\n✓ MOTOR data sent successfully!")
            print(f"  - Reading ID: {data['data']['id']}")
            print(f"  - Severity: {data['data']['severity']}")
            print(f"  - Backend Synced: {data['data']['backend_synced']}")
            print(f"  - Telemetry Type: {data['data']['telemetry_type']}")
            return True
        else:
            print(f"\n✗ Failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection Error!")
        print("Make sure Edge Service is running: python app.py")
        return False
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False


def verify_backend():
    """Check if backend is running and accessible."""
    print("\n=== Checking Backend ===")
    try:
        response = requests.get("http://localhost:8080/actuator/health", timeout=5)
        # 200 = OK, 401 = Requires auth but backend is running
        if response.status_code in [200, 401]:
            if response.status_code == 401:
                print("✓ Backend is running! (endpoint requires auth, but that's OK)")
            else:
                print("✓ Backend is running!")
            return True
        else:
            print(f"✗ Backend returned unexpected status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Backend is not running!")
        print("Start it with: ./mvnw spring-boot:run")
        return False


def verify_edge_service():
    """Check if Edge Service is running."""
    print("\n=== Checking Edge Service ===")
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✓ Edge Service is running!")
            return True
        else:
            print(f"✗ Edge Service returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Edge Service is not running!")
        print("Start it with: python app.py")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("ESP32 → Edge Service → Backend Integration Test")
    print("=" * 60)
    
    # Verify services are running
    backend_ok = verify_backend()
    edge_ok = verify_edge_service()
    
    if not backend_ok or not edge_ok:
        print("\n❌ Prerequisites not met. Please start the required services.")
        exit(1)
    
    # Run tests
    cabina_ok = test_cabina_data()
    motor_ok = test_motor_data()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Backend:        {'✓ Running' if backend_ok else '✗ Not running'}")
    print(f"Edge Service:   {'✓ Running' if edge_ok else '✗ Not running'}")
    print(f"CABINA Test:    {'✓ Passed' if cabina_ok else '✗ Failed'}")
    print(f"MOTOR Test:     {'✓ Passed' if motor_ok else '✗ Failed'}")
    
    if cabina_ok and motor_ok:
        print("\n✅ All tests passed! Integration is working correctly.")
        print("\nNext steps:")
        print("1. Check the database for new telemetry records")
        print("2. Test with Wokwi ESP32 simulators")
        print("3. Verify insights are being generated")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
