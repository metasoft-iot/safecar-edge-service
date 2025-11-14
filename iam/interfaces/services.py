"""REST API controllers for IAM context"""
from flask import Blueprint, request, jsonify
from iam.application.services import AuthApplicationService

iam_api = Blueprint('iam_api', __name__, url_prefix='/api/v1/auth')

# Initialize the authentication service
auth_service = AuthApplicationService()


def authenticate_request():
    """
    Authenticate incoming requests using device_id and API key.
    
    Checks for 'device_id' in JSON body and 'X-API-Key' in headers.
    
    Returns:
        None if authenticated, else a tuple response with error message.
    """
    device_id = request.json.get("device_id") if request.json else None
    api_key = request.headers.get('X-API-Key')
    
    if not device_id or not api_key:
        return jsonify({"error": "Missing device_id or API key"}), 401
    
    if not auth_service.authenticate(device_id, api_key):
        return jsonify({"error": "Invalid device_id or API key"}), 401
    
    return None


@iam_api.route('/devices', methods=['POST'])
def register_device():
    """
    Register a new device.
    
    Request body:
    {
        "device_id": "edge-device-001",
        "api_key": "your-api-key"
    }
    
    Returns:
        201: Device registered successfully
        400: Invalid request data
    """
    from datetime import datetime
    
    data = request.get_json()
    
    if not data or 'device_id' not in data or 'api_key' not in data:
        return jsonify({
            'error': 'Missing required fields: device_id, api_key'
        }), 400
    
    try:
        auth_service = AuthApplicationService()
        device = auth_service.register_device(
            device_id=data['device_id'],
            api_key=data['api_key']
        )
        
        # Handle both datetime objects and strings
        created_at_str = device.created_at.isoformat() if isinstance(device.created_at, datetime) else str(device.created_at)
        
        return jsonify({
            'message': 'Device registered successfully',
            'device_id': device.device_id,
            'created_at': created_at_str
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500


@iam_api.route('/devices/validate', methods=['POST'])
def validate_device():
    """
    Validate device credentials.
    
    Request body:
    {
        "device_id": "edge-device-001",
        "api_key": "your-api-key"
    }
    
    Returns:
        200: Device credentials are valid
        401: Invalid credentials
        400: Invalid request data
    """
    from datetime import datetime
    
    data = request.get_json()
    
    if not data or 'device_id' not in data or 'api_key' not in data:
        return jsonify({
            'error': 'Missing required fields: device_id, api_key'
        }), 400
    
    try:
        auth_service = AuthApplicationService()
        device = auth_service.authenticate_device(
            device_id=data['device_id'],
            api_key=data['api_key']
        )
        
        if device:
            # Handle both datetime objects and strings
            created_at_str = device.created_at.isoformat() if isinstance(device.created_at, datetime) else str(device.created_at)
            
            return jsonify({
                'valid': True,
                'device_id': device.device_id,
                'created_at': created_at_str
            }), 200
        else:
            return jsonify({
                'valid': False,
                'error': 'Invalid device credentials'
            }), 401
    
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500
