"""
Smart Irrigation System - Flask Web Dashboard
Provides web interface to monitor and control the irrigation system
"""

from flask import Flask, render_template, jsonify, request
from arduino_reader import arduino_reader
import threading
import time

app = Flask(__name__)

# Store system status
system_status = {
    'auto_mode': True,
    'manual_override': False,
    'manual_pump_status': False
}

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """API endpoint to get current sensor data"""
    current_data = arduino_reader.get_current_data()
    
    # Add system status to response
    response_data = {
        'sensor_data': current_data,
        'system_status': system_status,
        'history': arduino_reader.get_history()[-10:]  # Last 10 readings for chart
    }
    
    return jsonify(response_data)

@app.route('/api/control', methods=['POST'])
def control_system():
    """API endpoint to control the irrigation system"""
    global system_status
    
    data = request.get_json()
    
    if 'auto_mode' in data:
        system_status['auto_mode'] = data['auto_mode']
        system_status['manual_override'] = not data['auto_mode']
    
    if 'manual_pump' in data and system_status['manual_override']:
        system_status['manual_pump_status'] = data['manual_pump']
        # In a real system, you would send command to Arduino here
    
    return jsonify({'status': 'success', 'system_status': system_status})

@app.route('/api/history')
def get_history():
    """API endpoint to get full data history"""
    return jsonify(arduino_reader.get_history())

if __name__ == '__main__':
    # Start reading from Arduino
    if arduino_reader.start_reading():
        print("Arduino reader started successfully")
    else:
        print("Failed to start Arduino reader")
    
    # Start Flask app
    print("Starting Flask server...")
    print("Dashboard will be available at: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
