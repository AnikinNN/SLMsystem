#include <math.h>

void setup() {
  Serial.begin(115200);
  Serial.println("ready");
}

void loop() {
  if(Serial.available()){
    String income = Serial.readString();
    income.trim();
    if(income.substring(0,3) == "get"){
      int sensor_index = income.substring(4).toInt();
      String response = "FFFF000" + 
                        (String)((sensor_index  + 1)* 1000 + micros() % 1000 )+ 
                        "30";
      Serial.println(response);
    }
  }
}
