
/********************************************************************/
// First we include the libraries
#include <OneWire.h>
#include <DallasTemperature.h>
/********************************************************************/
// Data wire is plugged into pin 8 on the Arduino
#define ONE_WIRE_BUS 8
/********************************************************************/
// Setup a oneWire instance to communicate with any OneWire devices
// (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);
/********************************************************************/
// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);
/********************************************************************/

int ledPin1 = 13;
int ledPin2 = 7;
int soil_moistPin = 12;
int photoresistorPin = A0;
int soilSensorPin = A1;
int photoresistorValue;
int soilSensorValue;
String val;

void setup() {
   // start serial port
  Serial.begin(9600);
  sensors.begin();

  //leds
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  pinMode(soil_moistPin, OUTPUT);

}

void loop() {

  photoresistorValue = analogRead(photoresistorPin);  //photoresistor
  int temp = sensors.getTempCByIndex(0);
  sensors.requestTemperatures(); // Send the command to get temperature readings
  if(Serial.available()){
        val = Serial.readStringUntil('\n');

        //Green led on-off
        if(val == "green_led_on"){
          digitalWrite(ledPin2, HIGH);
        } else if (val == "green_led_off"){
          digitalWrite(ledPin2, LOW);
        }

        //Red led on-off
        if(val == "red_led_on"){
          digitalWrite(ledPin1, HIGH);
        } else if (val == "red_led_off"){
          digitalWrite(ledPin1, LOW);
        }

        //Temp
        if(val == "temperature"){
          Serial.println(sensors.getTempCByIndex(0));
        }

        //Light
        if(val == "light"){
          Serial.println(photoresistorValue);
        }

        //Soil
        if(val == "soil"){
          digitalWrite(soil_moistPin, HIGH);
          delay(3000);
          soilSensorValue = analogRead(soilSensorPin);
          Serial.println(soilSensorValue);
          //delay(2500);
          digitalWrite(soil_moistPin, LOW);
        }
        
    }
}
