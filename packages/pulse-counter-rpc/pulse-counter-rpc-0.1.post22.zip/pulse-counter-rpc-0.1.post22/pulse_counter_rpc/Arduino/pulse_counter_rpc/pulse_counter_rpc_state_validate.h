#ifndef ___OD_SENSOR_RPC_STATE_VALIDATE___
#define ___OD_SENSOR_RPC_STATE_VALIDATE___

namespace pulse_counter_rpc {
namespace state_validate {

template <typename NodeT>
struct OnStatePulseChannelChanged : public ScalarFieldValidator<uint32_t, 1> {
  typedef ScalarFieldValidator<uint32_t, 1> base_type;

  NodeT *node_p_;
  OnStatePulseChannelChanged() : node_p_(NULL) {
    this->tags_[0] = 2;
  }

  void set_node(NodeT &node) { node_p_ = &node; }
  virtual bool operator()(uint32_t &source, uint32_t target) {
    if (node_p_ != NULL) { return node_p_->on_state_pulse_channel_changed(source); }
    return false;
  }
};

template <typename NodeT>
struct OnStatePulseDirectionChanged : public ScalarFieldValidator<uint32_t, 1> {
  typedef ScalarFieldValidator<uint32_t, 1> base_type;

  NodeT *node_p_;
  OnStatePulseDirectionChanged() : node_p_(NULL) {
    this->tags_[0] = 3;
  }

  void set_node(NodeT &node) { node_p_ = &node; }
  virtual bool operator()(uint32_t &source, uint32_t target) {
    if (node_p_ != NULL) { return node_p_->on_state_pulse_direction_changed(); }
    return false;
  }
};

template <typename NodeT>
struct OnStatePulsePinChanged : public ScalarFieldValidator<int32_t, 1> {
  typedef ScalarFieldValidator<int32_t, 1> base_type;

  NodeT *node_p_;
  OnStatePulsePinChanged() : node_p_(NULL) {
    this->tags_[0] = 1;
  }

  void set_node(NodeT &node) { node_p_ = &node; }
  virtual bool operator()(int32_t &source, int32_t target) {
    if (node_p_ != NULL) { return node_p_->on_state_pulse_pin_changed(target, source); }
    return false;
  }
};

template <typename NodeT>
class Validator : public MessageValidator<3> {
public:
  OnStatePulseChannelChanged<NodeT> pulse_channel_;
  OnStatePulseDirectionChanged<NodeT> pulse_direction_;
  OnStatePulsePinChanged<NodeT> pulse_pin_;

  Validator() {
    register_validator(pulse_channel_);
    register_validator(pulse_direction_);
    register_validator(pulse_pin_);
  }

  void set_node(NodeT &node) {
    pulse_channel_.set_node(node);
    pulse_direction_.set_node(node);
    pulse_pin_.set_node(node);
  }
};

}  // namespace state_validate
}  // namespace pulse_counter_rpc

#endif  // #ifndef ___OD_SENSOR_RPC_STATE_VALIDATE___
    
