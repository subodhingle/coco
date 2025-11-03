#include <Arduino.h>
#line 1 "C:\\Users\\A\\Desktop\\smart_irrigation_system\\smart_irrigation_system.ino"
/*
Smart Irrigation System - Arduino Code
Reads soil moisture and controls water pump relay
*/

const int SOIL_MOISTURE_PIN = A0;
const int RELAY_PIN = 7;

int soilMoistureValue = 0;
int soilMoisturePercent = 0;
bool pumpStatus = false;

const int DRY_THRESHOLD = 30;
const int WET_THRESHOLD = 60;

#line 16 "C:\\Users\\A\\Desktop\\smart_irrigation_system\\smart_irrigation_system.ino"
void setup();
#line 24 "C:\\Users\\A\\Desktop\\smart_irrigation_system\\smart_irrigation_system.ino"
void loop();
#line 16 "C:\\Users\\A\\Desktop\\smart_irrigation_system\\smart_irrigation_system.ino"
void setup() {
  Serial.begin(9600);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH);
  Serial.println("Smart Irrigation System Started");
  delay(1000);
}

void loop() {
  soilMoistureValue = analogRead(SOIL_MOISTURE_PIN);
  soilMoisturePercent = map(soilMoistureValue, 300, 700, 0, 100);
  soilMoisturePercent = constrain(soilMoisturePercent, 0, 100);

  if (soilMoisturePercent < DRY_THRESHOLD && !pumpStatus) {
    digitalWrite(RELAY_PIN, LOW);
    pumpStatus = true;
  } else if (soilMoisturePercent > WET_THRESHOLD && pumpStatus) {
    digitalWrite(RELAY_PIN, HIGH);
    pumpStatus = false;
  }

  Serial.print("{");
  Serial.print("\"moisture\": ");
  Serial.print(soilMoisturePercent);
  Serial.print(", \"raw_value\": ");
  Serial.print(soilMoistureValue);
  Serial.print(", \"pump_status\": ");
  Serial.print(pumpStatus ? "true" : "false");
  Serial.print(", \"threshold_low\": ");
  Serial.print(DRY_THRESHOLD);
  Serial.print(", \"threshold_high\": ");
  Serial.print(WET_THRESHOLD);
  Serial.println("}");

  delay(2000);
}

