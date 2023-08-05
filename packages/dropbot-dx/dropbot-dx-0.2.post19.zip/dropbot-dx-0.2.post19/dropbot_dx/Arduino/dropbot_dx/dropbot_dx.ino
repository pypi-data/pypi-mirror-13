#include "Arduino.h"
#include "EEPROM.h"
#include "SPI.h"
#include "Wire.h"
#include "Servo.h"
#include "Memory.h"
#include "ArduinoRpc.h"
#include "nanopb.h"
#include "NadaMQ.h"
#include "CArrayDefs.h"
#include "RPCBuffer.h"
#include "NodeCommandProcessor.h"
#include "BaseNodeRpc.h"
#include "DropbotDx.h"
#include "Node.h"


dropbot_dx::Node node_obj;
dropbot_dx::CommandProcessor<dropbot_dx::Node> command_processor(node_obj);


void i2c_receive_event(int byte_count) { node_obj.i2c_handler_.receiver()(byte_count); }
void serialEvent() { node_obj.serial_handler_.receiver()(Serial.available()); }


void setup() {
  node_obj.begin();
  Wire.onReceive(i2c_receive_event);
}


void loop() {
#ifndef DISABLE_SERIAL
  /* Parse all new bytes that are available.  If the parsed bytes result in a
   * completed packet, pass the complete packet to the command-processor to
   * process the request. */
  if (node_obj.serial_handler_.packet_ready()) {
    node_obj.serial_handler_.process_packet(command_processor);
  }
#endif  // #ifndef DISABLE_SERIAL
  if (node_obj.i2c_handler_.packet_ready()) {
    node_obj.i2c_handler_.process_packet(command_processor);
  }
  node_obj.loop();
}
