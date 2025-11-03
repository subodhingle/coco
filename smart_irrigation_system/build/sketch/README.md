#line 1 "C:\\Users\\A\\Desktop\\smart_irrigation_system\\README.md"
FLIE-structure

smart_irrigation/
├── app.py
├── arduino_reader.py
├── templates/
│   └── index.html
├── static/
│   └── js/
│       └── chart.js
└── smart_irrigation.ino


1. Arduino reads soil moisture using a sensor and sends the data via serial to the computer.
2. Python (Flask) receives and stores this data in memory.
3. A live web dashboard displays soil moisture readings using Chart.js (line graph).
4. Include automatic motor (relay) ON/OFF logic based on soil moisture level.
5. Folder structure must include:
   - app.py (Flask server)
   - arduino_reader.py (reads serial data)
   - templates/index.html (Flask HTML)
   - static/js/chart.js (Chart.js frontend)
6. The dashboard must auto-refresh every few seconds using AJAX.
7. Use pyserial, Flask, and requests (give pip install instructions).
8. Add comments in the code explaining every part.
9. Make sure the dashboard runs locally at http://127.0.0.1:5000.
10. Include a section in the Flask app to show motor status (ON/OFF).
Hardware Connection Instructions
Components Needed:
Arduino Uno/Nano

🌿 Smart Irrigation System (Arduino + Python + Flask Dashboard)

A Smart Irrigation System that automatically controls a water pump based on soil moisture level and displays real-time data on a Flask-based web dashboard.

The system reads soil moisture using an analog sensor, controls the pump via relay, and provides live monitoring using Chart.js.

🧰 Components Required
Component	Quantity	Description
Arduino Uno / Nano	1	Microcontroller board
Soil Moisture Sensor (YL-69 or similar)	1	Measures soil moisture
Relay Module (5V)	1	Controls water pump
Water Pump (3–12V DC)	1	Used for irrigation
Jumper Wires	—	For connections
Breadboard	1	For prototyping
⚙️ Wiring Diagram
🪴 Soil Moisture Sensor
Pin	Connects To
VCC	5V
GND	GND
A0	Arduino A0
⚡ Relay Module
Pin	Connects To
VCC	5V
GND	GND
IN	Digital Pin 7
💧 Water Pump
Pin	Connects To
Positive	Relay NO (Normally Open)
Negative	GND
Power Source	External 5–12V DC (⚠️ Do not power pump from Arduino)
🚀 Installation & Setup
Step 1: Clone the Repository
git clone https://github.com/yourusername/Smart-Irrigation-System.git
cd Smart-Irrigation-System

Step 2: Install Python Dependencies
pip install flask pyserial requests

Step 3: Upload Arduino Code

Open Arduino IDE

Connect Arduino via USB

Open the smart_irrigation.ino sketch

Upload the code

Note the COM port (Windows) or /dev/tty* (Linux/Mac)

Step 4: Configure Serial Port

Open arduino_reader.py and update the port:

# For Windows:
arduino_reader = ArduinoReader(port='COM3')

# For Linux/Mac:
arduino_reader = ArduinoReader(port='/dev/ttyUSB0')

Step 5: Run the System
python app.py

Step 6: Access the Dashboard

Open your browser and go to:
👉 http://127.0.0.1:5000

🎯 How It Works

Arduino

Continuously reads soil moisture

Sends moisture value & pump status via serial

Controls pump automatically:

Pump ON → Moisture < 30%

Pump OFF → Moisture > 60%

Python + Flask

Reads data from Arduino via serial (pyserial)

Serves real-time JSON data to web dashboard

Hosts local web server on port 5000

Frontend (Chart.js)

Fetches data every 2 seconds (AJAX)

Displays real-time soil moisture graph

Shows pump status dynamically (ON/OFF)

⚙️ Calibration Tips

Find Sensor Range:

Dry air → ~0%

Water → ~100%

Adjust mapping in Arduino code:

soilMoisturePercent = map(soilMoistureValue, YOUR_DRY_VALUE, YOUR_WET_VALUE, 0, 100);


Set Moisture Thresholds:

const int DRY_THRESHOLD = 30;  // Below this pump turns ON
const int WET_THRESHOLD = 60;  // Above this pump turns OFF


Modify values based on your plant type and soil.

📊 Example Dashboard Preview
🌿 Smart Irrigation Dashboard
------------------------------
Soil Moisture: 45%
Pump Status: OFF
Real-Time Chart: (auto-updates every 2s)

🧠 Tech Stack

Hardware: Arduino UNO, YL-69 Sensor, Relay Module

Backend: Python Flask, PySerial

Frontend: HTML, JavaScript, Chart.js, AJAX

🛠️ Future Improvements

Add database (SQLite) to log historical readings

Include DHT11/DHT22 temperature and humidity sensors

Add rainfall sensor for more accuracy

Deploy on Raspberry Pi for standalone use
