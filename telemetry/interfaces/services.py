"""REST API controllers for Telemetry context"""
from flask import Blueprint, request, jsonify
from telemetry.application.services import TelemetryApplicationService

telemetry_api = Blueprint('telemetry_api', __name__, url_prefix='/api/v1/telemetry')


@telemetry_api.route('/samples', methods=['POST'])
def create_sensor_reading():
    """
    Create a new sensor reading from IoT device.
    
    Headers:
        X-Device-Id: Device identifier
        X-API-Key: Device API key
    
    Request body:
    {
        "temperature_celsius": 85.5,
        "gas_type": "methane",
        "gas_concentration_ppm": 450.0,
        "current_amperes": 2.3,
        "timestamp": "2025-11-13T10:30:00Z"
    }
    
    Returns:
        201: Sensor reading created successfully
        400: Invalid request data
        401: Unauthorized
    """
    # Get authentication headers
    device_id = request.headers.get('X-Device-Id')
    api_key = request.headers.get('X-API-Key')
    
    if not device_id or not api_key:
        return jsonify({
            'error': 'Missing authentication headers: X-Device-Id and X-API-Key required'
        }), 401
    
    # Get request data
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    try:
        telemetry_service = TelemetryApplicationService()
        result = telemetry_service.record_sensor_reading(
            device_id=device_id,
            api_key=api_key,
            temperature_celsius=data.get('temperature_celsius'),
            gas_type=data.get('gas_type'),
            gas_concentration_ppm=data.get('gas_concentration_ppm'),
            current_amperes=data.get('current_amperes'),
            timestamp=data.get('timestamp')
        )
        
        return jsonify({
            'message': 'Sensor reading recorded successfully',
            'data': result
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500


@telemetry_api.route('/readings/<int:reading_id>', methods=['GET'])
def get_reading(reading_id):
    """
    Get a sensor reading by ID.
    
    Returns:
        200: Sensor reading found
        404: Reading not found
    """
    try:
        telemetry_service = TelemetryApplicationService()
        reading = telemetry_service.get_reading_by_id(reading_id)
        
        if not reading:
            return jsonify({'error': 'Reading not found'}), 404
        
        return jsonify({
            'data': reading
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500


@telemetry_api.route('/vehicles/<int:vehicle_id>/readings', methods=['GET'])
def get_vehicle_readings(vehicle_id):
    """
    Get sensor readings for a vehicle.
    
    Query parameters:
        start_date: Start date (ISO format, optional)
        end_date: End date (ISO format, optional)
        limit: Maximum number of results (default: 100)
    
    Returns:
        200: List of sensor readings
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        
        telemetry_service = TelemetryApplicationService()
        readings = telemetry_service.get_vehicle_readings(
            vehicle_id=vehicle_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return jsonify({
            'vehicle_id': vehicle_id,
            'count': len(readings),
            'data': readings
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500


@telemetry_api.route('/stats', methods=['GET'])
def get_device_stats():
    """
    Get statistics for the authenticated device.
    
    Headers:
        X-Device-Id: Device identifier
        X-API-Key: Device API key
    
    Returns:
        200: Device statistics
        401: Unauthorized
    """
    device_id = request.headers.get('X-Device-Id')
    api_key = request.headers.get('X-API-Key')
    
    if not device_id or not api_key:
        return jsonify({
            'error': 'Missing authentication headers: X-Device-Id and X-API-Key required'
        }), 401
    
    try:
        telemetry_service = TelemetryApplicationService()
        stats = telemetry_service.get_device_statistics(device_id, api_key)
        
        return jsonify({
            'data': stats
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500
