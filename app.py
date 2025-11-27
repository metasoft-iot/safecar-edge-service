"""SafeCar Edge Service - Main Application.

This edge service processes IoT sensor data from two ESP32 devices and sends
telemetry to the SafeCar backend platform for analysis and alerting.

ESP32 (CABINA) - Located in car cabin:
- DHT11: Temperature and humidity monitoring
- MQ2: Gas detection (GLP, butane, propane, methane, alcohol, hydrogen)
- NEO6M: GPS module with EEPROM and reception antenna

ESP32 (MOTOR) - Located in engine compartment:
- DHT11: Temperature and humidity monitoring
- ACS712-05: Current sensor (Hall effect, 0-5 Amperes)
"""
from flask import Flask

import iam.application.services
from telemetry.interfaces.services import telemetry_api
from iam.interfaces.services import iam_api
from shared.infrastructure.database import init_db

app = Flask(__name__)
app.register_blueprint(iam_api)
app.register_blueprint(telemetry_api)

first_request = True


@app.before_request
def setup():
    """
    Initialize the database and create a test device on the first request.
    This ensures that the database is set up and a test device is available for authentication.
    :return:
    None
    """
    global first_request
    if first_request:
        first_request = False
        init_db()
        auth_application_service = iam.application.services.AuthApplicationService()
        auth_application_service.get_or_create_test_device()


@app.route('/')
def about_edge_service():
    return (
        'SafeCar Edge Service - Vehicle Telemetry Collection. '
        'Visit /api/v1/telemetry/samples to POST sensor data.'
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
