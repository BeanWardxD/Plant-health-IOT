What to do with BLE.ino:

First replace the pins with the ones you are actually using

int ldrPin = A1;  
int soilPin = A0;
int dhtPin = 13;

Make sure you have the right libraries and then upload it to your arduino

What to do with RPBLE.py:
This is the thingspeak API key you must change it to use it on your own channel

API_KEY = "ZOR5L68NGXEE6FUQ"


These relate to the arduino you must replace them with your arduinos mac addresss and the UUID you set

BLE_ADDRESS = "F4:12:FA:6F:34:6D"  
BLE_CHAR_UUID = "00002222-0000-1000-8000-00805f9b34fb" 


Once you have done that run it on a bluetooth capable device and it should connect with the arduino and start receiving data

Make sure Plants_AI.pkl is stored in the same place as the RPBLE.py file


What to do with the MATLAB script:

If you want to run the matlab script for your own channel replace the API key and channel ID with your own

readAPIKey = 'QGV1CM7R4YQ2DULB';
channelID = 3224928;
