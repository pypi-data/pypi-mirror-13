#ifndef ___DROPBOT_DX_STATE_VALIDATE___
#define ___DROPBOT_DX_STATE_VALIDATE___

namespace dropbot_dx {
namespace state_validate {

template <typename NodeT>
struct OnStateLightEnabledChanged : public ScalarFieldValidator<bool, 1> {
  typedef ScalarFieldValidator<bool, 1> base_type;

  NodeT *node_p_;
  OnStateLightEnabledChanged() : node_p_(NULL) {
    this->tags_[0] = 2;
  }

  void set_node(NodeT &node) { node_p_ = &node; }
  virtual bool operator()(bool &source, bool target) {
    if (node_p_ != NULL) { return node_p_->on_state_light_enabled_changed(source); }
    return false;
  }
};

template <typename NodeT>
struct OnStateMagnetEngagedChanged : public ScalarFieldValidator<bool, 1> {
  typedef ScalarFieldValidator<bool, 1> base_type;

  NodeT *node_p_;
  OnStateMagnetEngagedChanged() : node_p_(NULL) {
    this->tags_[0] = 1;
  }

  void set_node(NodeT &node) { node_p_ = &node; }
  virtual bool operator()(bool &source, bool target) {
    if (node_p_ != NULL) { return node_p_->on_state_magnet_engaged_changed(source); }
    return false;
  }
};

template <typename NodeT>
class Validator : public MessageValidator<2> {
public:
  OnStateLightEnabledChanged<NodeT> light_enabled_;
  OnStateMagnetEngagedChanged<NodeT> magnet_engaged_;

  Validator() {
    register_validator(light_enabled_);
    register_validator(magnet_engaged_);
  }

  void set_node(NodeT &node) {
    light_enabled_.set_node(node);
    magnet_engaged_.set_node(node);
  }
};

}  // namespace state_validate
}  // namespace dropbot_dx

#endif  // #ifndef ___DROPBOT_DX_STATE_VALIDATE___
    
