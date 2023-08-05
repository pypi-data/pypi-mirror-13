
/* #########################################################################
 * [2015-12-18 17:20:47.958000] THIS FILE IS AUTOGENERATED - DO NOT EDIT!
 * ######################################################################### */

/* Automatically generated nanopb constant definitions */
/* Generated by nanopb-0.3.2 at Fri Dec 18 17:20:47 2015. */

#include "config_pb.h"

#if PB_PROTO_HEADER_VERSION != 30
#error Regenerate this file with the current version of nanopb generator.
#endif

const uint32_t pulse_counter_rpc_Config_baud_rate_default = 115200u;
const uint32_t pulse_counter_rpc_Config_mux_channel_a_pin_default = 4u;
const uint32_t pulse_counter_rpc_Config_mux_channel_b_pin_default = 8u;
const int32_t pulse_counter_rpc_State_pulse_pin_default = -1;
const uint32_t pulse_counter_rpc_State_pulse_channel_default = 0u;
const uint32_t pulse_counter_rpc_State_pulse_direction_default = 3u;
const bool pulse_counter_rpc_State_pulse_count_enable_default = false;
const uint32_t pulse_counter_rpc_State_pulse_count_default = 0u;


const pb_field_t pulse_counter_rpc_Config_fields[6] = {
    PB_FIELD(  1, UINT32  , OPTIONAL, STATIC  , FIRST, pulse_counter_rpc_Config, serial_number, serial_number, 0),
    PB_FIELD(  2, UINT32  , OPTIONAL, STATIC  , OTHER, pulse_counter_rpc_Config, baud_rate, serial_number, &pulse_counter_rpc_Config_baud_rate_default),
    PB_FIELD(  3, UINT32  , OPTIONAL, STATIC  , OTHER, pulse_counter_rpc_Config, i2c_address, baud_rate, 0),
    PB_FIELD(  4, UINT32  , OPTIONAL, STATIC  , OTHER, pulse_counter_rpc_Config, mux_channel_a_pin, i2c_address, &pulse_counter_rpc_Config_mux_channel_a_pin_default),
    PB_FIELD(  5, UINT32  , OPTIONAL, STATIC  , OTHER, pulse_counter_rpc_Config, mux_channel_b_pin, mux_channel_a_pin, &pulse_counter_rpc_Config_mux_channel_b_pin_default),
    PB_LAST_FIELD
};

const pb_field_t pulse_counter_rpc_State_fields[6] = {
    PB_FIELD(  1, INT32   , OPTIONAL, STATIC  , FIRST, pulse_counter_rpc_State, pulse_pin, pulse_pin, &pulse_counter_rpc_State_pulse_pin_default),
    PB_FIELD(  2, UINT32  , OPTIONAL, STATIC  , OTHER, pulse_counter_rpc_State, pulse_channel, pulse_pin, &pulse_counter_rpc_State_pulse_channel_default),
    PB_FIELD(  3, UINT32  , OPTIONAL, STATIC  , OTHER, pulse_counter_rpc_State, pulse_direction, pulse_channel, &pulse_counter_rpc_State_pulse_direction_default),
    PB_FIELD(  4, BOOL    , OPTIONAL, STATIC  , OTHER, pulse_counter_rpc_State, pulse_count_enable, pulse_direction, &pulse_counter_rpc_State_pulse_count_enable_default),
    PB_FIELD(  5, UINT32  , OPTIONAL, STATIC  , OTHER, pulse_counter_rpc_State, pulse_count, pulse_count_enable, &pulse_counter_rpc_State_pulse_count_default),
    PB_LAST_FIELD
};


