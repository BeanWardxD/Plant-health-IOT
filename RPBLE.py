import asyncio
import time
import pickle
import os
import sklearn
import requests
import json
import pandas
from bleak import BleakClient

#Collection of constants used to connect with either arduino or thingspeak
API_KEY = "ZOR5L68NGXEE6FUQ"
THINGSPEAK_URL = "https://api.thingspeak.com/update"
MODEL_PATH = "Plants_AI.pkl"
BLE_ADDRESS = "F4:12:FA:6F:34:6D"  
BLE_CHAR_UUID = "00002222-0000-1000-8000-00805f9b34fb"  



async def est_ble(mac):
 
    while True:
        try:
            #This part is to set up a connection with the arduino
            client = BleakClient(mac)
            await client.connect()
            print("Connected via BLE")
            return client
        except Exception as e:
            print(f"Connection failed: {e}")
            await asyncio.sleep(1)  #Waits before retrying so it doesnt spam messages

async def recv_ble(client):
    likely_BLE_failure = 0
    while likely_BLE_failure < 6:
        try:
            #Waits to receive the JSON from the arduino then decodes it and tries again if it fails
            raw_bytes = await client.read_gatt_char(BLE_CHAR_UUID)
            line = raw_bytes.decode("utf-8").strip()
            if not line:
                continue
            useable_json = json.loads(line)
            return useable_json
        except Exception as e:
            print(f"BLE read or JSON decode failed: {e}")
            likely_BLE_failure += 1
            await asyncio.sleep(1)
        

def process(data, model):
    #Makes it a data frame which can be used with the model
    data = pandas.DataFrame([data])
    print(data)
    data['Predicted_Health_Status'] = model.predict(data)
    print(data['Predicted_Health_Status'])
    return data

def load_model(path):

        if not os.path.exists(path):  #Checks the model is even there
            print(f"Model file not found: {MODEL_PATH}")
        with open(path, "rb") as file:
                model = pickle.load(file)  #Loads pickle if its available
        print("Model loaded")
        return model
        #Since its critical to the program it will just crash if there is no model so the pi knows there is a problem

def send_to_thingspeak(data):
    #Assigns features of the dataframe to fields in thingspeak
    #If the dataframe had more than one record this would be a problem so iloc 0
    #is there just incase
    payload = {
        "api_key": API_KEY,
        "field1": data['Soil_Moisture'].iloc[0],
        "field2": data['Ambient_Temperature'].iloc[0],
        "field3": data['Humidity'].iloc[0],
        "field4": data['Light_Intensity'].iloc[0],
        "field5": data['Predicted_Health_Status'].iloc[0]
        
    }


    try:
        #Attempts to send the payload and determins if it was sent or not
        response = requests.post(THINGSPEAK_URL, data=payload, timeout=5)
        if response.status_code == 200:
            if response.text.strip() == "0":
                print("ThingSpeak update failed (probably invalid data).")
            else:
                print(f"Data sent successfully. Entry ID: {response.text.strip()}")
        else:
            print(f"HTTP Error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")

async def main():
    model = load_model(MODEL_PATH)
    while True:
        
        client = await est_ble(BLE_ADDRESS)

        try:
            while True:
                useable_json = await recv_ble(client)
 

                final_data = process(useable_json, model)

       
                send_to_thingspeak(final_data)

                await asyncio.sleep(16)  #ThingSpeak only lets you send data every 15s I set it to 16 just to be safe though
        except Exception as e:
            #When something goes wrong this sets it back on track by ending the loop
            print(f"Reconnecting: {e}")
            await client.disconnect()
            await asyncio.sleep(1)



if __name__ == "__main__":
    asyncio.run(main())

