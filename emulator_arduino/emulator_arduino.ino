void setup() {
  Serial.begin(2000000);
  Serial.println("ready");
}

void loop() {
  if(Serial.available() >= 4){
    String income = Serial.readStringUntil('\n');
    income.trim();
    if(income.substring(0,3) == "get"){
      int sensor_index = income.substring(3).toInt();
      String response = "FFFF" + 
                        // sign
                        String(sensor_index % 2 << 3) + 
                        // some int value in length of 6
                        (String)((sensor_index  + 1) * 100000 + millis() % 100000 )+ 
                        // decimal point
                        "30\n";
      // emulate time for obtain data from indicator
      delay(40);
      Serial.print(response);
    }
  }
}
