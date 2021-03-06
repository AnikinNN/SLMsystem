#include "Digimatic.h"

 Digimatic::Digimatic(uint8_t clk, uint8_t data, uint8_t req)
 {
	clk_pin = clk;
	data_pin = data;
	req_pin = req;

  // configure pins
  pinMode(clk_pin, INPUT_PULLUP);
  pinMode(data_pin, INPUT_PULLUP);
  pinMode(req_pin, INPUT);
 }
 
void Digimatic::fetch()
{
  // configure pins
  pinMode(req_pin, OUTPUT);

  // set req_pin to initial state
  digitalWrite(req_pin, HIGH);

  // clk_pin watchers
  int curr_status = 0;
  int prev_status = digitalRead(clk_pin);
  int toggle_counter = 0;
  int cycle_counter = 0;
  
  clean_data();

  // variable to implement timeout
  unsigned long start_time = millis();

  // toggle req_pin to start
  digitalWrite(req_pin, LOW);

  while(millis() - start_time < 1000 && toggle_counter < 104){
    cycle_counter++;
    curr_status = digitalRead(clk_pin);
    if(curr_status != prev_status){
      digitalWrite(req_pin, HIGH);
      prev_status = curr_status;
      toggle_counter++;
      if(curr_status == 0){
        data_buffer[toggle_counter / 2] = digitalRead(data_pin);
        // bitWrite(data[toggle_counter / 8], toggle_counter / 2 % 4, digitalRead(data_pin));
      }
    }
  }

  pinMode(req_pin, INPUT);

  //validation
  if(toggle_counter != 104){
    //error ocurred
    clean_data();
  } else{
    for(int i = 0; i < 52; i++){
      bitWrite(data[i / 4], i % 4, data_buffer[i]);
    }
  }
//  Serial.print(cycle_counter);
//  Serial.print(" ");
//  Serial.print(toggle_counter / 8);
//  Serial.print(" ");
}

void Digimatic::print_data()
{
  fetch();
  for(int i = 0; i < 13; i++){
    Serial.print(data[i], HEX);
  }
}

void Digimatic::clean_data(){
  for(int i = 0; i < 13; i++ ) {
    data[i] = 0b0;
    for(int k = 0; k < 4; k++){
      data_buffer[i * 4 + k] = 0;
    }
  }

  
}
