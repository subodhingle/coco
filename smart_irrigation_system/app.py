"""
Smart Irrigation System - Flask Web Dashboard
Provides web interface to monitor and control the irrigation system
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from arduino_reader import arduino_reader
from datetime import datetime
from threading import Lock
import threading
import time

app = Flask(__name__)
CORS(app)

_lock = Lock()

# Store system status
system_status = {
    'auto_mode': True,
    'manual_override': False,
    'manual_pump_status': False
}

# current sensor data and system state
_sensor_data = {
    "moisture": None,
    "raw_value": None,
    "pump_status": False,
    "threshold_low": 30,
    "threshold_high": 60
}
_system_status = {"auto_mode": True}
_history = []  # list of {"timestamp": iso_str, "moisture": value}
_MAX_HISTORY = 500

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

@app.route("/api/ingest", methods=["POST"])
def ingest():
    """
    Expects the raw JSON from the serial device:
    {"moisture": 100, "raw_value": 1022, "pump_status": false, "threshold_low": 30, "threshold_high": 60}
    """
    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify({"error": "invalid json"}), 400

    with _lock:
        # update sensor data fields that exist in payload
        for k in ("moisture", "raw_value", "pump_status", "threshold_low", "threshold_high"):
            if k in payload:
                _sensor_data[k] = payload[k]

        # append to history (timestamp as ISO)
        _history.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "moisture": _sensor_data.get("moisture")
        })
        # truncate
        if len(_history) > _MAX_HISTORY:
            del _history[0: len(_history) - _MAX_HISTORY]

    return jsonify({"ok": True}), 200

@app.route("/api/control", methods=["POST"])
def control():
    """
    Accepts { "auto_mode": bool } or { "manual_pump": bool }
    """
    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify({"error": "invalid json"}), 400

    with _lock:
        if "auto_mode" in payload:
            _system_status["auto_mode"] = bool(payload["auto_mode"])
            # if enabling auto-mode, manual pump toggles should be ignored by system
        if "manual_pump" in payload:
            # manual_pump true -> force pump on, false -> pump off
            _sensor_data["pump_status"] = bool(payload["manual_pump"])
            # when manual pump toggled, we are effectively in manual mode
            _system_status["auto_mode"] = False

    return jsonify({"ok": True, "system_status": _system_status, "sensor_data": _sensor_data})

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
