#include "Digimatic.h"

 Digimatic::Digimatic(uint8_t clk, uint8_t data, uint8_t req)
 {
	clk_pin = clk;
	data_pin = data;
	req_pin = req;
 }
 
void Digimatic::fetch()
{
  // configure pins
  pinMode(clk_pin, INPUT_PULLUP);
  pinMode(data_pin, INPUT_PULLUP);
  pinMode(req_pin, OUTPUT);

  // set req_pin to initial state
  digitalWrite(req_pin, HIGH);

  // clk_pin watchers
  int curr_status = 0;
  int prev_status = digitalRead(clk_pin);
  int toggle_counter = 0;
  
  clean_data();

  // variable to implement timeout
  unsigned long start_time = millis();

  // toggle req_pin to start
  digitalWrite(req_pin, LOW);

  while(millis() - start_time < 110 && toggle_counter < 13 * 4 * 2){
    curr_status = digitalRead(clk_pin);
    if(curr_status != prev_status){
      digitalWrite(req_pin, HIGH);
      prev_status = curr_status;
      toggle_counter++;
      if(curr_status == 0){
        bitWrite(data[toggle_counter / 8], toggle_counter / 2 % 4, digitalRead(data_pin));
      }
    }
  }

  pinMode(req_pin, INPUT);

  //validation
  if(toggle_counter != 13 * 4 * 2){
    //error ocurred
    clean_data();
  }
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
  }
}
