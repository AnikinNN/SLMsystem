void setup() {
  Serial.begin(115200);
  Serial.println("ready");
}

void loop() {
  if(Serial.available() > 2){
    String income = Serial.readStringUntil('\n');
    income.trim();
    if(income.substring(0,3) == "get"){
      String response = "";
      for(int i = 0; i < 2; i++){
        int sensor_index = i;
        response += "FFFF" + 
                    // sign
                    String(sensor_index % 2 << 3) + 
                    // some int value in length of 6
                    (String)((sensor_index  + 1) * 100000 + millis() % 100000 )+ 
                    // decimal point
                    "30 ";
        // emulate time for obtain data from indicator
        delay(40);
      }
      response += "\n";
      Serial.print(response);
    }
  }
}
