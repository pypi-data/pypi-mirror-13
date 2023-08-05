#ifndef ___DROPBOT_DX_CONFIG_VALIDATE___
#define ___DROPBOT_DX_CONFIG_VALIDATE___

namespace dropbot_dx {
namespace config_validate {

template <typename NodeT>
struct OnConfigBaudRateChanged : public ScalarFieldValidator<uint32_t, 1> {
  typedef ScalarFieldValidator<uint32_t, 1> base_type;

  NodeT *node_p_;
  OnConfigBaudRateChanged() : node_p_(NULL) {
    this->tags_[0] = 2;
  }

  void set_node(NodeT &node) { node_p_ = &node; }
  virtual bool operator()(uint32_t &source, uint32_t target) {
    if (node_p_ != NULL) { return node_p_->on_config_baud_rate_changed(source); }
    return false;
  }
};

template <typename NodeT>
struct OnConfigI2cAddressChanged : public ScalarFieldValidator<uint32_t, 1> {
  typedef ScalarFieldValidator<uint32_t, 1> base_type;

  NodeT *node_p_;
  OnConfigI2cAddressChanged() : node_p_(NULL) {
    this->tags_[0] = 3;
  }

  void set_node(NodeT &node) { node_p_ = &node; }
  virtual bool operator()(uint32_t &source, uint32_t target) {
    if (node_p_ != NULL) { return node_p_->on_config_i2c_address_changed(source); }
    return false;
  }
};

template <typename NodeT>
struct OnConfigSerialNumberChanged : public ScalarFieldValidator<uint32_t, 1> {
  typedef ScalarFieldValidator<uint32_t, 1> base_type;

  NodeT *node_p_;
  OnConfigSerialNumberChanged() : node_p_(NULL) {
    this->tags_[0] = 1;
  }

  void set_node(NodeT &node) { node_p_ = &node; }
  virtual bool operator()(uint32_t &source, uint32_t target) {
    if (node_p_ != NULL) { return node_p_->on_config_serial_number_changed(source); }
    return false;
  }
};

template <typename NodeT>
class Validator : public MessageValidator<3> {
public:
  OnConfigBaudRateChanged<NodeT> baud_rate_;
  OnConfigI2cAddressChanged<NodeT> i2c_address_;
  OnConfigSerialNumberChanged<NodeT> serial_number_;

  Validator() {
    register_validator(baud_rate_);
    register_validator(i2c_address_);
    register_validator(serial_number_);
  }

  void set_node(NodeT &node) {
    baud_rate_.set_node(node);
    i2c_address_.set_node(node);
    serial_number_.set_node(node);
  }
};

}  // namespace config_validate
}  // namespace dropbot_dx

#endif  // #ifndef ___DROPBOT_DX_CONFIG_VALIDATE___
    
