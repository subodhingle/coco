"""
Smart Irrigation System - Arduino Serial Reader
Reads data from Arduino via serial port and provides it to Flask app
"""

import serial
import json
import threading
import time
from datetime import datetime

class ArduinoReader:
    def __init__(self, port='COM3', baudrate=9600):
        """
        Initialize Arduino serial connection
        Change 'COM3' to your actual port (e.g., '/dev/ttyUSB0' on Linux/Mac)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.current_data = {
            'moisture': 0,
            'raw_value': 0,
            'pump_status': False,
            'timestamp': datetime.now().isoformat()
        }
        self.data_history = []
        self.max_history = 50  # Keep last 50 readings
        self.running = False
        self.thread = None
        
    def connect(self):
        """Establish connection to Arduino"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            print(f"Connected to Arduino on {self.port}")
            return True
        except Exception as e:
            print(f"Error connecting to Arduino: {e}")
            return False
    
    def start_reading(self):
        """Start the background thread for reading data"""
        if not self.connect():
            return False
            
        self.running = True
        self.thread = threading.Thread(target=self._read_loop)
        self.thread.daemon = True
        self.thread.start()
        return True
    
    def stop_reading(self):
        """Stop the background reading thread"""
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
    
    def _read_loop(self):
        """Background thread that continuously reads from Arduino"""
        while self.running:
            try:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    
                    if line and line.startswith('{'):
                        # Parse JSON data from Arduino
                        data = json.loads(line)
                        data['timestamp'] = datetime.now().isoformat()
                        
                        # Update current data
                        self.current_data = data
                        
                        # Add to history
                        self.data_history.append(data.copy())
                        
                        # Keep only recent history
                        if len(self.data_history) > self.max_history:
                            self.data_history.pop(0)
                            
                        print(f"Moisture: {data['moisture']}% | Pump: {'ON' if data['pump_status'] else 'OFF'}")
                        
            except json.JSONDecodeError:
                print("Error parsing JSON from Arduino")
            except Exception as e:
                print(f"Error reading from Arduino: {e}")
                time.sleep(2)  # Wait before retrying
    
    def get_current_data(self):
        """Get the most recent sensor data"""
        return self.current_data
    
    def get_history(self):
        """Get all historical sensor data"""
        return self.data_history

# Global instance
arduino_reader = ArduinoReader()
