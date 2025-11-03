"""
Smart Irrigation System - Flask Web Dashboard
Provides web interface to monitor and control the irrigation system
Integrated with Arduino serial communication
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
from threading import Lock, Thread
import serial
import json
import time

app = Flask(__name__)
CORS(app)

_lock = Lock()

# Serial connection configuration
SERIAL_PORT = 'COM6'
BAUD_RATE = 9600
ser = None

# Store system status
system_status = {
    'auto_mode': True,
    'manual_override': False,
    'manual_pump_status': False
}

# Current sensor data and system state
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

def read_arduino_data():
    """
    Background thread function to continuously read data from Arduino
    """
    global ser
    
    try:
        ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
        print(f"Connected to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud")
        
        while True:
            if ser.in_waiting > 0:
                try:
                    # Read line from Arduino
                    data = ser.readline().decode('utf-8', errors='replace').strip()
                    print(f"Received from Arduino: {data}")
                    
                    # Try to parse as JSON
                    try:
                        payload = json.loads(data)
                        
                        # Update sensor data with lock
                        with _lock:
                            # Update sensor data fields that exist in payload
                            for k in ("moisture", "raw_value", "pump_status", "threshold_low", "threshold_high"):
                                if k in payload:
                                    _sensor_data[k] = payload[k]
                            
                            # Append to history
                            if _sensor_data.get("moisture") is not None:
                                _history.append({
                                    "timestamp": datetime.utcnow().isoformat() + "Z",
                                    "moisture": _sensor_data.get("moisture")
                                })
                                
                                # Truncate history if needed
                                if len(_history) > _MAX_HISTORY:
                                    del _history[0: len(_history) - _MAX_HISTORY]
                        
                        print(f"Updated sensor data: moisture={_sensor_data.get('moisture')}%, pump={_sensor_data.get('pump_status')}")
                        
                    except json.JSONDecodeError:
                        # If not JSON, just log it as raw data
                        print(f"Non-JSON data: {data}")
                        
                except Exception as e:
                    print(f"Error reading/parsing data: {e}")
            
            time.sleep(0.1)  # Small delay to prevent CPU spinning
            
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        print(f"Could not connect to {SERIAL_PORT}. Please check:")
        print("1. Arduino is connected")
        print("2. Correct COM port")
        print("3. No other program is using the port")
    except Exception as e:
        print(f"Unexpected error in Arduino reader: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Serial connection closed")

def send_command_to_arduino(command):
    """
    Send command to Arduino via serial
    command should be a dict that will be sent as JSON
    """
    global ser
    if ser and ser.is_open:
        try:
            cmd_str = json.dumps(command) + '\n'
            ser.write(cmd_str.encode('utf-8'))
            print(f"Sent to Arduino: {cmd_str.strip()}")
            return True
        except Exception as e:
            print(f"Error sending command to Arduino: {e}")
            return False
    return False

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """
    Returns what index.html expects:
    {
      "sensor_data": {...},
      "system_status": {...},
      "history": [{timestamp, moisture}, ...]
    }
    """
    with _lock:
        return jsonify({
            "sensor_data": _sensor_data.copy(),
            "system_status": _system_status.copy(),
            "history": list(_history)
        })

@app.route("/api/ingest", methods=["POST"])
def ingest():
    """
    Manual endpoint for injecting data (kept for backward compatibility or testing)
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
        if _sensor_data.get("moisture") is not None:
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
    Sends commands to Arduino if needed
    """
    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify({"error": "invalid json"}), 400

    with _lock:
        if "auto_mode" in payload:
            auto_mode = bool(payload["auto_mode"])
            _system_status["auto_mode"] = auto_mode
            system_status['auto_mode'] = auto_mode
            
            # Send command to Arduino
            send_command_to_arduino({"auto_mode": auto_mode})
            
        if "manual_pump" in payload:
            # manual_pump true -> force pump on, false -> pump off
            manual_pump = bool(payload["manual_pump"])
            _sensor_data["pump_status"] = manual_pump
            # when manual pump toggled, we are effectively in manual mode
            _system_status["auto_mode"] = False
            system_status['auto_mode'] = False
            
            # Send command to Arduino
            send_command_to_arduino({"manual_pump": manual_pump, "auto_mode": False})

    return jsonify({"ok": True, "system_status": _system_status, "sensor_data": _sensor_data})

@app.route('/api/history')
def get_history():
    """API endpoint to get full data history"""
    with _lock:
        return jsonify(list(_history))

@app.route('/api/status')
def get_status():
    """Check if Arduino connection is active"""
    global ser
    is_connected = ser is not None and ser.is_open
    return jsonify({
        "arduino_connected": is_connected,
        "port": SERIAL_PORT,
        "baud_rate": BAUD_RATE
    })

if __name__ == '__main__':
    print("="*60)
    print("Smart Irrigation System - Starting...")
    print("="*60)
    
    # Start Arduino reader thread
    arduino_thread = Thread(target=read_arduino_data, daemon=True)
    arduino_thread.start()
    print(f"Arduino reader thread started on {SERIAL_PORT}")
    
    # Give the serial connection a moment to establish
    time.sleep(2)
    
    print("\n" + "="*60)
    print("Flask Dashboard starting...")
    print("Dashboard available at: http://127.0.0.1:5000")
    print("="*60)
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        if ser and ser.is_open:
            ser.close()
        print("Server stopped.")