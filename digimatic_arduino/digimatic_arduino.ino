#include "Digimatic.h"

// define pins
#define CLK_PIN 2
#define REQ_PIN 3
#define DATA_PIN 6

// initialize Digimatic
Digimatic sensors[] = {Digimatic(CLK_PIN, DATA_PIN, REQ_PIN), 
                     Digimatic(7, 8, 9)};

void setup()
{
  Serial.begin(115200);
}

void loop()
{
  if(Serial.available()){
    String income = Serial.readString();
    income.trim();
    if(income.substring(0,3) == "get"){
      int sensor_index = income.substring(4).toInt();
      sensors[sensor_index].get_data();
    }
  }
}
