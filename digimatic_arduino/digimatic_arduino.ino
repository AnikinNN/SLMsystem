#include "Digimatic.h"

// define pins
#define CLK_PIN 2
#define REQ_PIN 4
#define DATA_PIN 3

// initialize Digimatic
Digimatic sensors[] = {Digimatic(2, 4, 3), 
                     Digimatic(6, 5, 7)};

void setup()
{
  Serial.begin(2000000);
  Serial.println("ready");

}

void loop()
{
  if(Serial.available() > 3){
    String income = Serial.readStringUntil('\n');
    income.trim();
    if(income.substring(0,3) == "get"){
      sensors[0].print_data();
      Serial.print(" ");
      sensors[1].print_data();
      Serial.print("\n");
    }
  }
}
