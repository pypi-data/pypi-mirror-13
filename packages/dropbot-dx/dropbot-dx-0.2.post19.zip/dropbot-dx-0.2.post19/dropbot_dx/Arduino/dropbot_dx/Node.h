#ifndef ___NODE__H___
#define ___NODE__H___

#include <stdint.h>
#include <Arduino.h>
#include <Servo.h>
#include <Wire.h>
#include <EEPROM.h>
#include <NadaMQ.h>
#include <CArrayDefs.h>
#include "RPCBuffer.h"  // Define packet sizes
#include "DropbotDx/Properties.h"  // Define package name, URL, etc.
#include <BaseNodeRpc/BaseNode.h>
#include <BaseNodeRpc/BaseNodeEeprom.h>
#include <BaseNodeRpc/BaseNodeI2c.h>
#include <BaseNodeRpc/BaseNodeConfig.h>
#include <BaseNodeRpc/BaseNodeState.h>
#include <BaseNodeRpc/BaseNodeSerialHandler.h>
#include <BaseNodeRpc/BaseNodeI2cHandler.h>
#include <BaseNodeRpc/I2cHandler.h>
#include <BaseNodeRpc/SerialHandler.h>
#include <pb_validate.h>
#include <pb_eeprom.h>
#include "dropbot_dx_config_validate.h"
#include "dropbot_dx_state_validate.h"
#include "DropbotDx/config_pb.h"


namespace dropbot_dx {
const size_t FRAME_SIZE = (3 * sizeof(uint8_t)  // Frame boundary
                           - sizeof(uint16_t)  // UUID
                           - sizeof(uint16_t)  // Payload length
                           - sizeof(uint16_t));  // CRC

class Node;

typedef nanopb::EepromMessage<dropbot_dx_Config,
                              config_validate::Validator<Node> > config_t;
typedef nanopb::Message<dropbot_dx_State,
                        state_validate::Validator<Node> > state_t;

class Node :
  public BaseNode,
  public BaseNodeEeprom,
  public BaseNodeI2c,
  public BaseNodeConfig<config_t>,
  public BaseNodeState<state_t>,
#ifndef DISABLE_SERIAL
  public BaseNodeSerialHandler,
#endif  // #ifndef DISABLE_SERIAL
  public BaseNodeI2cHandler<base_node_rpc::i2c_handler_t> {
public:
  typedef PacketParser<FixedPacket> parser_t;

  static const uint16_t BUFFER_SIZE = 128;  // >= longest property string

  uint8_t buffer_[BUFFER_SIZE];
  uint32_t tick_count_;
  int32_t target_position_;
  Servo servo_;

  Node() : BaseNode(), BaseNodeConfig<config_t>(dropbot_dx_Config_fields),
           BaseNodeState<state_t>(dropbot_dx_State_fields) {}

  UInt8Array get_buffer() { return UInt8Array_init(sizeof(buffer_), buffer_); }
  /* This is a required method to provide a temporary buffer to the
   * `BaseNode...` classes. */

  void begin();
  void set_i2c_address(uint8_t value);  // Override to validate i2c address

  /****************************************************************************
   * # User-defined methods #
   *
   * Add new methods below.  When Python package is generated using the
   * command, `paver sdist` from the project root directory, the signatures of
   * the methods below will be scanned and code will automatically be generated
   * to support calling the methods from Python over a serial connection.
   *
   * e.g.
   *
   *     bool less_than(float a, float b) { return a < b; }
   *
   * See [`arduino_rpc`][1] and [`base_node_rpc`][2] for more details.
   *
   * [1]: https://github.com/wheeler-microfluidics/arduino_rpc
   * [2]: https://github.com/wheeler-microfluidics/base_node_rpc
   */
  uint8_t servo_read() { return servo_.read(); }
  void servo_write(uint8_t angle) { servo_.write(angle); }
  void servo_write_microseconds(uint16_t us) { servo_.writeMicroseconds(us); }
  bool servo_attached() { return servo_.attached(); }
  void servo_detach() { servo_.detach(); }
  void servo_attach(uint8_t servo_pin) { servo_.attach(servo_pin); }

  bool magnet_engaged() { return servo_.read() == config_._.engaged_angle; }

  bool light_override() {
    pinMode(config_._.light_override_pin, INPUT);
    return (config_._.light_override_enabled &&
            digitalRead(config_._.light_override_pin));
  }
  bool light_enabled() { return digitalRead(config_._.light_pin); }

  void loop() {
    if (state_._.magnet_engaged && !magnet_engaged()) {
      _magnet_engage();
    } else if (!state_._.magnet_engaged && magnet_engaged()) {
      _magnet_disengage();
    }
    // If light override is active, light will be turned off regardless of the
    // `light_enabled` state setting.
    if (state_._.light_enabled && !light_override() && !light_enabled()) {
      _light_enable();
    } else if ((!state_._.light_enabled || light_override()) &&
               light_enabled()) {
      _light_disable();
    }
  }

  bool on_config_light_pin_changed(uint32_t new_value) {
    // Configure light pin as output.
    pinMode(new_value, OUTPUT);
    return true;
  }

  bool on_state_magnet_engaged_changed(bool new_value) {
    /* Update magnet position based on updated setting. */
    if (new_value) { _magnet_engage(); }
    else { _magnet_disengage(); }
    // Trigger update of `magnet_engaged` field in local state structure.
    return true;
  }

  bool on_state_light_enabled_changed(bool new_value) {
    /* Update state of light output based on updated setting. */
    if (new_value) { _light_enable(); }
    else { _light_disable(); }
    // Trigger update of `light_enabled` field in local state structure.
    return true;
  }

  // Local methods
  // TODO: Should likely be private, but need to add private handling to code
  // scraper/generator.
  void _magnet_engage() { servo_.write(config_._.engaged_angle); }
  void _magnet_disengage() { servo_.write(config_._.disengaged_angle); }
  void _light_enable() { digitalWrite(config_._.light_pin, HIGH); }
  void _light_disable() { digitalWrite(config_._.light_pin, LOW); }
};

}  // namespace dropbot_dx


#endif  // #ifndef ___NODE__H___
