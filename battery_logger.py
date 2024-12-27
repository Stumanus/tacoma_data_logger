#!/bin/python

from datetime import datetime
import sqlite3
from epevermodbus.driver import EpeverChargeController

controller = EpeverChargeController('/dev/ttyUSB0',1)

#finish formatting the data tuple, decide how to unpack Battery Status, Charging Equip. Status, 
data = {
        'datetime' : str(datetime.now()),
        #Stats:
        'solar_voltage_V' : f'{controller.get_solar_voltage()}',
        'solar_current_A' : f'{controller.get_solar_current()}',
        'solar_power_W' : f'{controller.get_solar_power()}',
        'load_voltage_V' : f'{controller.get_load_voltage()}',
        'load_current_A' : f'{controller.get_load_current()}',
        'load_power_W' : f'{controller.get_load_power()}',
        'battery_voltage_V' : f'{controller.get_battery_voltage()}',
        'battery_current_A' : f'{controller.get_battery_current()}',
        'battery_power_W' : f'controller.get_battery_power()}',
        'battery_soc_%' : f'{controller.get_battery_state_of_charge()}',
        'battery_temp_C' : f'{controller.get_battery_temperature()}',
        'remote_battery_temp_C' : f'{controller.get_remote_battery_temperature()}'
        'controller_temp_C' : f'{controller.get_controller_temperature()}',
        'battery_status' : f'{controller.get_battery_status()}',
        'charging_equipment_status' : f'{controller.get_charging_equipment_status()}',
        'discharging_equipment_status' : f'{controller.get_discharging_equipment_status()}'
        'day_time' : f'{controller.is_day()}',
        'night_time' : f'{controller.is_night()}',
        'max_batt_voltage_today_V' : f'{controller.get_maximum_battery_voltage_today()}'
        'min_batt_voltage_today_V' : f'{controller.get_minimum_battery_voltage_today()}'
        'max_pv_voltage_today_V' : f'{controller.get_maximum_pv_voltage_today()}',
        'min_pv_voltage_today_V' : f'{controller.get_minimum_pv_voltage_today()}',
        'device_overtemp_status' : f'controller.is_device_over_temperature()}',
        'energy_consumed_today_kWh' : f'controller.get_consumed_energy_today()}',
        'energy_consumed_this_month_kWh' : f'{controller.get_consumed_energy_this_month()}',
        'energy_consumed_this_year_kWh' : f'{controller.get_consumed_energy_this_year()}',
        'energy_consumed_total_kWh' : f'{controller.get_total_consumed_energy()}',
        'energy_generated_today_kWh' : f'{controller.get_generated_energy_today()}',
        'energy_generated_this_month_kWh' : f'{controller.get_generated_energy_this_month()}',
        'energy_generated_this_year_kWh' : f'{controller.get_generated_energy_this_year()}',
        'energy_generated_total_kWh' : f'{controller.get_total_generated_energy()}',
        'current_device_time' : f'{controller.get_rtc()}',
        #Battery Parameters:
        'rated_charging_current_A' : f'{controller.get_rated_charging_current()}',
        'rated_load_current_A' : f'{controller.get_rated_load_current()}',
        'battery_real_rated_voltage_V' : f'{controller.get_battery_real_rated_voltage()}',
        'battery_type' : f'{controller.get_battery_type()}',
        'battery_capacity_AH' : f'{controller.get_battery_capacity()}',
        'temperature_compensation_coefficient_mV/C/Cell' : f'{controller.get_temperature_compensation_coefficient()}',
        'over_voltage_disconnect_voltage_V' : f'{controller.get_over_voltage_disconnect_voltage()}V',
        'charging_limit_voltage_V' : f'{controller.get_charging_limit_voltage()}',
        'over_voltage_reconnect_voltage_V' : f'{controller.get_over_voltage_reconnect_voltage()}'
        'equalize_charging_voltage_V' : f'{controller.get_equalize_charging_voltage()}',
        'boost_charging_voltage_V' : f'{controller.get_boost_charging_voltage()}',
        'float_charging_voltage_V' : f'{controller.get_float_charging_voltage()}',
        'boost_reconnect_charging_voltage_V' : f'{controller.get_boost_reconnect_charging_voltage()}',
        'low_voltage_reconnect_voltage_V' : f'{controller.get_low_voltage_reconnect_voltage()}',
        'under_voltage_recover_voltage_V' : f'{controller.get_under_voltage_recover_voltage()}',
        'under_voltage_warning_voltage_V' : f'{controller.get_under_voltage_warning_voltage()}',
        'low_voltage_disconnect_voltage_V' : f'{controller.get_low_voltage_disconnect_voltage()}V',
        'discharge_limit_voltage_V' : f'{controller.get_discharging_limit_voltage()}',
        'battery_rated_voltage_V' : f'{controller.get_battery_rated_voltage()}',
        'default_load_on/off_in_manual_mode' : f'{controller.get_default_load_on_off_in_manual_mode()}',
        'equalize_duration_min' : f'{controller.get_equalize_duration()}',
        'boost_duration_min' : f'{controller.get_boost_duration()}',
        'battery_discharge_%' : f'{controller.get_battery_discharge()}',
        'battery_charge_%' : f'{controller.get_battery_charge()}',
        'charging_mode' : f'{controller.get_charging_mode()}'
}

data_tuple = tuple(list(data.values()))
column_tuple = tuple(list(data.keys()))    

conn = sqlite3.connect('battery.db')
cur = conn.cursor()

tables = [x[0] for x in cur.execute('SELECT name FROM sqlite_master').fetchall()]
if 'battery' not in tables:
    cur.execute(f'CREATE TABLE battery{column_tuple}')

placeholders = ('?, ' * len(data))[:-2]
cur.execute(f'INSERT INTO battery VALUES({placeholders})',data_tuple)
