#ifndef Digimatic_h
#define Digimatic_h

#include <stdint.h>
#include <Arduino.h>

#define byte uint8_t

class Digimatic
{

public:
  // initializes measurement tool
  Digimatic(byte clk_pin, 
            byte data_pin, 
            byte req_pin);
  
  // requests and stores current measurement
  void fetch();
  // fetches and prints current measurement
  void print_data();
  // fills data by zeros
  void clean_data();

  // array to store data
  byte data[13];

  // pins
	byte req_pin;
	byte clk_pin;
	byte data_pin;
};

#endif
