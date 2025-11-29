"""
Flask API for Crisis Response Coordinator Agent
Deployment-ready REST API with /detect endpoint
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.coordinator_agent import CrisisCoordinator

app = Flask(__name__)
CORS(app)  # Enable CORS for web clients

# Initialize coordinator
coordinator = CrisisCoordinator()

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Crisis Response Coordinator',
        'version': '1.0',
        'endpoints': {
            '/detect': 'POST - Detect and respond to crisis',
            '/cases': 'GET - List active cases',
            '/case/<id>': 'GET - Get specific case details'
        }
    })

@app.route('/detect', methods=['POST'])
def detect_crisis():
    """
    Main crisis detection endpoint
    
    Request body:
    {
        "crisis_description": "string",
        "country": "USA" (optional)
    }
    
    Response:
    {
        "case_id": "CASE-00001",
        "classification": {...},
        "response": "formatted response text",
        "timestamp": "ISO timestamp"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'crisis_description' not in data:
            return jsonify({
                'error': 'Missing crisis_description in request body'
            }), 400
        
        crisis_description = data['crisis_description']
        country = data.get('country', 'USA')
        
        # Process crisis
        response = coordinator.handle_crisis(crisis_description, country)
        
        # Get the latest case
        cases = coordinator.list_active_cases()
        latest_case = cases[-1] if cases else None
        
        return jsonify({
            'success': True,
            'case_id': latest_case['id'] if latest_case else None,
            'classification': latest_case['classification'] if latest_case else None,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/cases', methods=['GET'])
def list_cases():
    """List all active cases"""
    try:
        cases = coordinator.list_active_cases()
        return jsonify({
            'success': True,
            'total_cases': len(cases),
            'cases': cases
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/case/<case_id>', methods=['GET'])
def get_case(case_id):
    """Get specific case details"""
    try:
        case = coordinator.get_case_status(case_id)
        
        if not case:
            return jsonify({
                'error': f'Case {case_id} not found',
                'success': False
            }), 404
        
        return jsonify({
            'success': True,
            'case': case
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Detailed health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'protocols_loaded': sum(len(v) for v in coordinator.protocols.values()),
            'active_cases': len(coordinator.active_cases),
            'api_configured': coordinator.model is not None,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
