#ifndef Digimatic_h
#define Digimatic_h

#include <stdint.h>

#define byte uint8_t

class Digimatic
{

public:
  //initialize
  Digimatic(byte clk_pin, byte data_pin, byte req_pin);
  // requests and returns current measurement
  void fetch(void);
  bool units_mm(void);         // true = mm; false = in
  bool units_in(void);         // true = in; false = mm
  byte decimal_places(void); 	 // digits after the decimal point
  double looptime(void);
  void print_data(void);         // prints rawdata to Serial
  void parse_measure(void);
  double get_value();
  byte rawdata[13];
  int error; 
  double cur_value;


protected:
	byte req_pin;
	byte clk_pin;
	byte data_pin;
	double looptime_ms;  
};

#endif
