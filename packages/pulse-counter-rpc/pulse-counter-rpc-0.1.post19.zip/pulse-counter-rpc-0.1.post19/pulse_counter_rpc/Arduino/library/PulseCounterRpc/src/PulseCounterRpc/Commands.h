
/* #########################################################################
 * [2015-12-18 17:20:50.915000] THIS FILE IS AUTOGENERATED - DO NOT EDIT!
 * ######################################################################### */
#ifndef ___PULSE_COUNTER_RPC__COMMANDS___
#define ___PULSE_COUNTER_RPC__COMMANDS___

#include "CArrayDefs.h"



namespace pulse_counter_rpc {


typedef struct __attribute__((packed)) {
} BaseNodeSoftwareVersionRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} BaseNodeSoftwareVersionResponse;

typedef struct __attribute__((packed)) {
} PackageNameRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} PackageNameResponse;

typedef struct __attribute__((packed)) {
} DisplayNameRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} DisplayNameResponse;

typedef struct __attribute__((packed)) {
} ManufacturerRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} ManufacturerResponse;

typedef struct __attribute__((packed)) {
} SoftwareVersionRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} SoftwareVersionResponse;

typedef struct __attribute__((packed)) {
} UrlRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} UrlResponse;

typedef struct __attribute__((packed)) {
} MicrosecondsRequest;

typedef struct __attribute__((packed)) {
  uint32_t result;
} MicrosecondsResponse;

typedef struct __attribute__((packed)) {
} MillisecondsRequest;

typedef struct __attribute__((packed)) {
  uint32_t result;
} MillisecondsResponse;

typedef struct __attribute__((packed)) {
  uint16_t us;
} DelayUsRequest;

typedef struct __attribute__((packed)) {
} DelayUsResponse;

typedef struct __attribute__((packed)) {
  uint16_t ms;
} DelayMsRequest;

typedef struct __attribute__((packed)) {
} DelayMsResponse;

typedef struct __attribute__((packed)) {
} RamFreeRequest;

typedef struct __attribute__((packed)) {
  uint32_t result;
} RamFreeResponse;

typedef struct __attribute__((packed)) {
  uint8_t pin;
  uint8_t mode;
} PinModeRequest;

typedef struct __attribute__((packed)) {
} PinModeResponse;

typedef struct __attribute__((packed)) {
  uint8_t pin;
} DigitalReadRequest;

typedef struct __attribute__((packed)) {
  uint8_t result;
} DigitalReadResponse;

typedef struct __attribute__((packed)) {
  uint8_t pin;
  uint8_t value;
} DigitalWriteRequest;

typedef struct __attribute__((packed)) {
} DigitalWriteResponse;

typedef struct __attribute__((packed)) {
  uint8_t pin;
} AnalogReadRequest;

typedef struct __attribute__((packed)) {
  uint16_t result;
} AnalogReadResponse;

typedef struct __attribute__((packed)) {
  uint8_t pin;
  uint8_t value;
} AnalogWriteRequest;

typedef struct __attribute__((packed)) {
} AnalogWriteResponse;

typedef struct __attribute__((packed)) {
  UInt8Array array;
} ArrayLengthRequest;

typedef struct __attribute__((packed)) {
  uint16_t result;
} ArrayLengthResponse;

typedef struct __attribute__((packed)) {
  UInt32Array array;
} EchoArrayRequest;

typedef struct __attribute__((packed)) {
  UInt32Array result;
} EchoArrayResponse;

typedef struct __attribute__((packed)) {
  UInt8Array msg;
} StrEchoRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} StrEchoResponse;

typedef struct __attribute__((packed)) {
} MaxSerialPayloadSizeRequest;

typedef struct __attribute__((packed)) {
  int32_t result;
} MaxSerialPayloadSizeResponse;

typedef struct __attribute__((packed)) {
  uint16_t address;
  UInt8Array data;
} UpdateEepromBlockRequest;

typedef struct __attribute__((packed)) {
} UpdateEepromBlockResponse;

typedef struct __attribute__((packed)) {
  uint16_t address;
  uint16_t n;
} ReadEepromBlockRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} ReadEepromBlockResponse;

typedef struct __attribute__((packed)) {
} EepromE2endRequest;

typedef struct __attribute__((packed)) {
  uint32_t result;
} EepromE2endResponse;

typedef struct __attribute__((packed)) {
} I2cAddressRequest;

typedef struct __attribute__((packed)) {
  uint8_t result;
} I2cAddressResponse;

typedef struct __attribute__((packed)) {
} I2cBufferSizeRequest;

typedef struct __attribute__((packed)) {
  uint16_t result;
} I2cBufferSizeResponse;

typedef struct __attribute__((packed)) {
} I2cScanRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} I2cScanResponse;

typedef struct __attribute__((packed)) {
} I2cAvailableRequest;

typedef struct __attribute__((packed)) {
  int16_t result;
} I2cAvailableResponse;

typedef struct __attribute__((packed)) {
} I2cReadByteRequest;

typedef struct __attribute__((packed)) {
  int8_t result;
} I2cReadByteResponse;

typedef struct __attribute__((packed)) {
  uint8_t address;
  uint8_t n_bytes_to_read;
} I2cRequestFromRequest;

typedef struct __attribute__((packed)) {
  int8_t result;
} I2cRequestFromResponse;

typedef struct __attribute__((packed)) {
  uint8_t address;
  uint8_t n_bytes_to_read;
} I2cReadRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} I2cReadResponse;

typedef struct __attribute__((packed)) {
  uint8_t address;
  UInt8Array data;
} I2cWriteRequest;

typedef struct __attribute__((packed)) {
} I2cWriteResponse;

typedef struct __attribute__((packed)) {
} I2cEnableBroadcastRequest;

typedef struct __attribute__((packed)) {
} I2cEnableBroadcastResponse;

typedef struct __attribute__((packed)) {
} I2cDisableBroadcastRequest;

typedef struct __attribute__((packed)) {
} I2cDisableBroadcastResponse;

typedef struct __attribute__((packed)) {
} MaxI2cPayloadSizeRequest;

typedef struct __attribute__((packed)) {
  uint32_t result;
} MaxI2cPayloadSizeResponse;

typedef struct __attribute__((packed)) {
  uint8_t address;
  UInt8Array data;
} I2cRequestRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} I2cRequestResponse;

typedef struct __attribute__((packed)) {
} I2cPacketResetRequest;

typedef struct __attribute__((packed)) {
} I2cPacketResetResponse;

typedef struct __attribute__((packed)) {
} LoadConfigRequest;

typedef struct __attribute__((packed)) {
} LoadConfigResponse;

typedef struct __attribute__((packed)) {
} SaveConfigRequest;

typedef struct __attribute__((packed)) {
} SaveConfigResponse;

typedef struct __attribute__((packed)) {
} ResetConfigRequest;

typedef struct __attribute__((packed)) {
} ResetConfigResponse;

typedef struct __attribute__((packed)) {
} SerializeConfigRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} SerializeConfigResponse;

typedef struct __attribute__((packed)) {
  UInt8Array serialized;
} UpdateConfigRequest;

typedef struct __attribute__((packed)) {
  uint8_t result;
} UpdateConfigResponse;

typedef struct __attribute__((packed)) {
  uint32_t new_value;
} OnConfigSerialNumberChangedRequest;

typedef struct __attribute__((packed)) {
  bool result;
} OnConfigSerialNumberChangedResponse;

typedef struct __attribute__((packed)) {
  uint32_t new_value;
} OnConfigBaudRateChangedRequest;

typedef struct __attribute__((packed)) {
  bool result;
} OnConfigBaudRateChangedResponse;

typedef struct __attribute__((packed)) {
  uint32_t new_value;
} OnConfigI2cAddressChangedRequest;

typedef struct __attribute__((packed)) {
  bool result;
} OnConfigI2cAddressChangedResponse;

typedef struct __attribute__((packed)) {
} ResetStateRequest;

typedef struct __attribute__((packed)) {
} ResetStateResponse;

typedef struct __attribute__((packed)) {
} SerializeStateRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} SerializeStateResponse;

typedef struct __attribute__((packed)) {
  UInt8Array serialized;
} UpdateStateRequest;

typedef struct __attribute__((packed)) {
  uint8_t result;
} UpdateStateResponse;

typedef struct __attribute__((packed)) {
} GetBufferRequest;

typedef struct __attribute__((packed)) {
  UInt8Array result;
} GetBufferResponse;

typedef struct __attribute__((packed)) {
} BeginRequest;

typedef struct __attribute__((packed)) {
} BeginResponse;

typedef struct __attribute__((packed)) {
  uint8_t value;
} SetI2cAddressRequest;

typedef struct __attribute__((packed)) {
} SetI2cAddressResponse;

typedef struct __attribute__((packed)) {
} LoopRequest;

typedef struct __attribute__((packed)) {
} LoopResponse;

typedef struct __attribute__((packed)) {
  uint32_t mux_channel_a_pin;
} OnConfigMuxChannelAPinChangedRequest;

typedef struct __attribute__((packed)) {
  bool result;
} OnConfigMuxChannelAPinChangedResponse;

typedef struct __attribute__((packed)) {
  uint32_t mux_channel_b_pin;
} OnConfigMuxChannelBPinChangedRequest;

typedef struct __attribute__((packed)) {
  bool result;
} OnConfigMuxChannelBPinChangedResponse;

typedef struct __attribute__((packed)) {
  int32_t old_pulse_pin;
  int32_t pulse_pin;
} OnStatePulsePinChangedRequest;

typedef struct __attribute__((packed)) {
  bool result;
} OnStatePulsePinChangedResponse;

typedef struct __attribute__((packed)) {
} OnStatePulseDirectionChangedRequest;

typedef struct __attribute__((packed)) {
  bool result;
} OnStatePulseDirectionChangedResponse;

typedef struct __attribute__((packed)) {
  uint32_t pulse_channel;
} OnStatePulseChannelChangedRequest;

typedef struct __attribute__((packed)) {
  bool result;
} OnStatePulseChannelChangedResponse;

typedef struct __attribute__((packed)) {
  uint8_t pulse_pin;
} SetPulsePinRequest;

typedef struct __attribute__((packed)) {
} SetPulsePinResponse;

typedef struct __attribute__((packed)) {
  uint32_t duration_ms;
} CountPulsesRequest;

typedef struct __attribute__((packed)) {
  int32_t result;
} CountPulsesResponse;

typedef struct __attribute__((packed)) {
} StartPulseCountRequest;

typedef struct __attribute__((packed)) {
} StartPulseCountResponse;

typedef struct __attribute__((packed)) {
} StopPulseCountRequest;

typedef struct __attribute__((packed)) {
  uint32_t result;
} StopPulseCountResponse;



static const int CMD_BASE_NODE_SOFTWARE_VERSION = 0x00;
static const int CMD_PACKAGE_NAME = 0x01;
static const int CMD_DISPLAY_NAME = 0x02;
static const int CMD_MANUFACTURER = 0x03;
static const int CMD_SOFTWARE_VERSION = 0x04;
static const int CMD_URL = 0x05;
static const int CMD_MICROSECONDS = 0x06;
static const int CMD_MILLISECONDS = 0x07;
static const int CMD_DELAY_US = 0x08;
static const int CMD_DELAY_MS = 0x09;
static const int CMD_RAM_FREE = 0x0a;
static const int CMD_PIN_MODE = 0x0b;
static const int CMD_DIGITAL_READ = 0x0c;
static const int CMD_DIGITAL_WRITE = 0x0d;
static const int CMD_ANALOG_READ = 0x0e;
static const int CMD_ANALOG_WRITE = 0x0f;
static const int CMD_ARRAY_LENGTH = 0x10;
static const int CMD_ECHO_ARRAY = 0x11;
static const int CMD_STR_ECHO = 0x12;
static const int CMD_MAX_SERIAL_PAYLOAD_SIZE = 0xff;
static const int CMD_UPDATE_EEPROM_BLOCK = 0x1fe;
static const int CMD_READ_EEPROM_BLOCK = 0x1ff;
static const int CMD_EEPROM_E2END = 0x200;
static const int CMD_I2C_ADDRESS = 0x2fe;
static const int CMD_I2C_BUFFER_SIZE = 0x2ff;
static const int CMD_I2C_SCAN = 0x300;
static const int CMD_I2C_AVAILABLE = 0x301;
static const int CMD_I2C_READ_BYTE = 0x302;
static const int CMD_I2C_REQUEST_FROM = 0x303;
static const int CMD_I2C_READ = 0x304;
static const int CMD_I2C_WRITE = 0x305;
static const int CMD_I2C_ENABLE_BROADCAST = 0x306;
static const int CMD_I2C_DISABLE_BROADCAST = 0x307;
static const int CMD_MAX_I2C_PAYLOAD_SIZE = 0x3fc;
static const int CMD_I2C_REQUEST = 0x3fd;
static const int CMD_I2C_PACKET_RESET = 0x3fe;
static const int CMD_LOAD_CONFIG = 0x4fb;
static const int CMD_SAVE_CONFIG = 0x4fc;
static const int CMD_RESET_CONFIG = 0x4fd;
static const int CMD_SERIALIZE_CONFIG = 0x4fe;
static const int CMD_UPDATE_CONFIG = 0x4ff;
static const int CMD_ON_CONFIG_SERIAL_NUMBER_CHANGED = 0x500;
static const int CMD_ON_CONFIG_BAUD_RATE_CHANGED = 0x501;
static const int CMD_ON_CONFIG_I2C_ADDRESS_CHANGED = 0x502;
static const int CMD_RESET_STATE = 0x5fa;
static const int CMD_SERIALIZE_STATE = 0x5fb;
static const int CMD_UPDATE_STATE = 0x5fc;
static const int CMD_GET_BUFFER = 0x6f9;
static const int CMD_BEGIN = 0x6fa;
static const int CMD_SET_I2C_ADDRESS = 0x6fb;
static const int CMD_LOOP = 0x6fc;
static const int CMD_ON_CONFIG_MUX_CHANNEL_A_PIN_CHANGED = 0x6fd;
static const int CMD_ON_CONFIG_MUX_CHANNEL_B_PIN_CHANGED = 0x6fe;
static const int CMD_ON_STATE_PULSE_PIN_CHANGED = 0x6ff;
static const int CMD_ON_STATE_PULSE_DIRECTION_CHANGED = 0x700;
static const int CMD_ON_STATE_PULSE_CHANNEL_CHANGED = 0x701;
static const int CMD_SET_PULSE_PIN = 0x702;
static const int CMD_COUNT_PULSES = 0x703;
static const int CMD_START_PULSE_COUNT = 0x704;
static const int CMD_STOP_PULSE_COUNT = 0x705;

}  // namespace pulse_counter_rpc



#endif  // ifndef ___PULSE_COUNTER_RPC__COMMANDS___
