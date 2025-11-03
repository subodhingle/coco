# library install 
# pip install pyserial


import serial

# Set up the serial connection (adjust baudrate as needed)
ser = serial.Serial('COM6', baudrate=9600, timeout=1)  # Use correct baudrate!

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8', errors='replace').strip()
            print(f"Received: {data}")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()