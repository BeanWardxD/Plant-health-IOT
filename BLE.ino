#include "DHT.h"
#include <ArduinoBLE.h> 

int ldrPin = A1;  
int soilPin = A0;
int dhtPin = 13;
int waterMoisture = 260;
int airMoisture = 1010;


#define DHTTYPE DHT11
DHT dht(dhtPin, DHTTYPE);


//Sets IDs so the Pi can connect
BLEService plantService("1111");
BLEStringCharacteristic sensorCharacteristic("2222", BLERead | BLENotify, 200);

void setup() {
  Serial.begin(9600);
  dht.begin();
  
  //Start BLE
  if (!BLE.begin()) {
    Serial.println("BLE start failed");
    while (1);
  }

  //Settings other devices can see
  BLE.setLocalName("UnoR4_PlantSensor");
  
  BLE.setAdvertisedService(plantService);
  plantService.addCharacteristic(sensorCharacteristic);
  BLE.addService(plantService);
  
  //This lets other devices (the pi) see it
  BLE.advertise();
  
  Serial.println("Waiting for connections");
}

void loop() {
  //Searches for BLE connections
  BLEDevice central = BLE.central();
  
  if (central) {
    Serial.print("Connected: ");
    Serial.println(central.address());
    
    while (central.connected()) {
      BLE.poll();
      //Reads sensors
      float humidity = dht.readHumidity();
      float tempC = dht.readTemperature();
      int ldrValue = analogRead(ldrPin);
      float soilValue = analogRead(soilPin);
      //Serial.print(soilValue);
      if (soilValue < waterMoisture){
            soilValue = waterMoisture;
      }
      else if(soilValue > airMoisture){
            soilValue = airMoisture;
      }
      float soilZeroed = (soilValue - waterMoisture);
      //Serial.print(soilZeroed);
      float soilFlipped= (soilZeroed/(airMoisture-waterMoisture))*100;
      //Serial.print(soilFlipped);
      float soilMoisture = 100-soilFlipped;
      //Prints so you know they are working
      Serial.print("Humidity: ");
      Serial.print(humidity);
      Serial.print("% | Temperature: ");
      Serial.print(tempC);
      Serial.print("°C | Light: ");
      Serial.print(ldrValue);
      Serial.print(" | Soil Moisture: ");
      Serial.println(soilMoisture);
      
      //Creates and sends JSON so Pi can process it
      String json = "{";
      json += "\"Soil_Moisture\":" + String(soilMoisture) + ",";
      json += "\"Ambient_Temperature\":" + String(tempC) + ",";
      json += "\"Humidity\":" + String(humidity) + ",";
      json += "\"Light_Intensity\":" + String(ldrValue);
      //json += "\"Nitrogen_Level\":" + String(0) + ",";
      //json += "\"Phosphorus_Level\":" + String(0) + ",";
      //json += "\"Potassium_Level\":" + String(0);
      json += "}";
      
      sensorCharacteristic.writeValue(json);
    
      BLE.poll();
      delay(200); //Proper delay is built into the pi since its dealing with thinkspeak
    }
    
    Serial.print("Disconnected: ");
    Serial.println(central.address());
  }
}
