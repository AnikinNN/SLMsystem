#include "Digimatic.h"

// initialize Digimatic
Digimatic sensors[] = {Digimatic(2, 3, 4), 
                     Digimatic(6, 5, 7)};

void setup()
{
  Serial.begin(115200);
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
