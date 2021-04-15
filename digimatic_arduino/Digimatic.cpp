#include <Arduino.h>
#include "Digimatic.h"
#include <stdint.h>


 Digimatic::Digimatic(uint8_t clk, uint8_t data, uint8_t req)
 {
	clk_pin = clk;
	data_pin = data;
	req_pin = req;
	pinMode(clk_pin, INPUT);
	pinMode(data_pin, INPUT);
	pinMode(req_pin, OUTPUT);
	digitalWrite(req_pin,LOW);
  error = 0;
 }
 
void Digimatic::fetch()
{
  // clear rawdata
  for(int i = 0; i < 13; i++ ) {
    rawdata[i] = 0;
  }
  error = 0;

  // trigger request
	digitalWrite(req_pin,HIGH);
  unsigned int start_time = micros();
  // wait for response on request
  while(true){
    if(digitalRead(clk_pin) == HIGH){
      break;
      }
    if(micros() - start_time > 100000){
      error = 1;
      //Serial.println("Error");
      break;
    }
  }
  if(error == 0){
    // return to initial state
    digitalWrite(req_pin, LOW);
    // obtain data  
    for(int i = 0; i < 13; i++ ) {
      int k = 0;
      for (int j = 0; j < 4; j++) {
        while( digitalRead(clk_pin) == LOW) {
        } // hold until clock is high or timeout
        while( digitalRead(clk_pin) == HIGH) { 
        } // hold until clock is low
        bitWrite(k, j, (digitalRead(data_pin) & 0x1)); // read data bits, and reverse order )
      }
      // store data
      rawdata[i] = k;
    }
  }
}

void Digimatic::parse_measure(){
  unsigned long start_time = micros();
  
  fetch();

  start_time = micros() - start_time;
  looptime_ms = (double)start_time/1000.0;
  
  // calculate value
  cur_value = rawdata[5] * 100000 +
              rawdata[6] * 10000 +
              rawdata[7] * 1000 +
              rawdata[8] * 100 +
              rawdata[9] * 10 +
              rawdata[10];
  // apply decimal point
  for(int i = 0; i < rawdata[11]; i++){
        cur_value /= 10;
      }
  // apply sign
  if(rawdata[4] == 8)
    cur_value = -cur_value;
}

double Digimatic::get_value(){
    fetch();
    parse_measure();
    return cur_value;
}

void Digimatic::print_data()
{
  fetch();
  for(int i = 0; i < 13; i++){
    Serial.print(rawdata[i], HEX);
  }
}

bool Digimatic::units_mm()
{
	return (rawdata[12] == 0);
}

bool Digimatic::units_in()
{
	return (rawdata[12] == 1);
}

byte Digimatic::decimal_places()
{
	return rawdata[11];
}

double Digimatic::looptime()
{
	return looptime_ms;
}
