#!/bin/python

from datetime import datetime
import sqlite3
from epevermodbus.driver import EpeverChargeController

controller = EpeverChargeController('/dev/ttyUSB0',1)
logging_interval = 30

def main():
    while True:
        time.sleep(logging_interval)
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
                'battery_power_W' : f'{controller.get_battery_power()}',
                'battery_soc_%' : f'{controller.get_battery_state_of_charge()}',
                'battery_temp_C' : f'{controller.get_battery_temperature()}',
                'remote_battery_temp_C' : f'{controller.get_remote_battery_temperature()}',
                'controller_temp_C' : f'{controller.get_controller_temperature()}',
                'max_batt_voltage_today_V' : f'{controller.get_maximum_battery_voltage_today()}'
                'min_batt_voltage_today_V' : f'{controller.get_minimum_battery_voltage_today()}'
                'max_pv_voltage_today_V' : f'{controller.get_maximum_pv_voltage_today()}',
                'min_pv_voltage_today_V' : f'{controller.get_minimum_pv_voltage_today()}',
                'energy_consumed_today_kWh' : f'{controller.get_consumed_energy_today()}',
                'energy_consumed_this_month_kWh' : f'{controller.get_consumed_energy_this_month()}',
                'energy_consumed_this_year_kWh' : f'{controller.get_consumed_energy_this_year()}',
                'energy_consumed_total_kWh' : f'{controller.get_total_consumed_energy()}',
                'energy_generated_today_kWh' : f'{controller.get_generated_energy_today()}',
                'energy_generated_this_month_kWh' : f'{controller.get_generated_energy_this_month()}',
                'energy_generated_this_year_kWh' : f'{controller.get_generated_energy_this_year()}',
                'energy_generated_total_kWh' : f'{controller.get_total_generated_energy()}',
        }

                #Device Status
        battery_status = controller.get_battery_status()
        charging_equipment_status = controller.get_charging_equipment_status()
        discharging_equipment_status = controller.get_discharging_equipment_status()

        equip_data = {
                'current_device_time' : f'{controller.get_rtc()}',
                'device_overtemp_status' : f'{controller.is_device_over_temperature()}',
                #Battery Status
                'wrong_id_for_rated_voltage' : battery_status['wrong_identification_for_rated_voltage'],
                'battery_inner_resistance_abnormal' : battery_status['battery_inner_resistence_abnormal'],
                'temperature_warning_status' : battery_status['temperature_warning_status'],
                'battery_status' : battery_status['battery_status'],
                #Charging Equipment Status 
                'charging_status' : charging_equipment_status['charging_status'],
                'charging_input_voltage_status' : charging_equipment_status['input_voltage_status'],
                'charging_mosfet_is_short_circuit' : charging_equipment_status['charging_mosfet_is_short_circuit'],
                'charging_or_anti_reverse_mosfet_is_open_circuit' : charging_equipment_status['charging_or_anti_reverse_mosfet_is_open_circuit'], 
                'anti_reverse_mosfet_is_short_circuit' : charging_equipment_status['anti_reverse_mosfet_is_short_circuit'],
                'input_over_current' : charging_equipment_status['input_over_current'],
                'load_over_current' : charging_equipment_status['load_over_current'],
                'load_short_circuit' : charging_equipment_status['load_short_circuit'],
                'load_mosfet_short_circuit' : charging_equipment_status['load_mosfet_short_circuit'],
                'disequilibrium_in_three_circuits' : charging_equipment_status['disequilibrium_in_three_circuits'],
                'pv_input_short_circuit' : charging_equipment_status['pv_input_short_circuit'],
                'charge_running' : charging_equipment_status['running'],
                #Discharging Equipment Status
                'discharging_input_voltage_status' : discharging_equipment_status['input_voltage_status'],
                'output_power_load' : discharging_equipment_status['output_power_load'],
                'short_circuit' : discharging_equipment_status['short_circuit'],
                'unable_to_discharge' : discharging_equipment_status['unable_to_discharge'],
                'unable_to_stop_discharging' : discharging_equipment_status['unable_to_stop_discharging'],
                'output_voltage_abnormal' : discharging_equipment_status['output_voltage_abnormal'],
                'input_over_voltage' : discharging_equipment_status['input_over_voltage'],
                'short_circuit_in_high_voltage_side' : discharging_equipment_status['short_circuit_in_high_voltage_side'],
                'boost_over_voltage' : discharging_equipment_status['boost_over_voltage'],
                'output_over_voltage' : discharging_equipment_status['output_over_voltage'],
                'discharge_fault' : discharging_equipment_status['fault'],
                'discharge_running' : discharging_equipment_status['running']
        }

        data_tuple = tuple(list(data.values()))
        column_tuple = tuple(list(data.keys()))

        equip_data_tuple = tuple(list(equip_data.values()))
        equip_column_tuple = tuple(list(equip_data.keys()))

        conn = sqlite3.connect('battery.db')
        cur = conn.cursor()

        tables = [x[0] for x in cur.execute('SELECT name FROM sqlite_master').fetchall()]
        if 'battery' not in tables:
            cur.execute(f'CREATE TABLE battery{column_tuple}')
        if 'status' not in tables:
            cur.execute(f'CREATE TABLE status{equip_column_tuple}')

        placeholders = ('?, ' * len(data))[:-2]
        cur.execute(f'INSERT INTO battery VALUES({placeholders})',data_tuple)

        placeholders = ('?, ' * len(equip_data))[:-2]
        cur.execute(f'INSERT INTO status VALUES({placeholders})',equip_data_tuple)

        conn.commit()
        conn.close()

if __name__ == '__main__':
    main()

#Data dict template
#data = {
#        'datetime' : str(datetime.now()),
#        #Stats:
#        'solar_voltage_V' : f'{controller.get_solar_voltage()}',
#        'solar_current_A' : f'{controller.get_solar_current()}',
#        'solar_power_W' : f'{controller.get_solar_power()}',
#        'load_voltage_V' : f'{controller.get_load_voltage()}',
#        'load_current_A' : f'{controller.get_load_current()}',
#        'load_power_W' : f'{controller.get_load_power()}',
#        'battery_voltage_V' : f'{controller.get_battery_voltage()}',
#        'battery_current_A' : f'{controller.get_battery_current()}',
#        'battery_power_W' : f'controller.get_battery_power()}',
#        'battery_soc_%' : f'{controller.get_battery_state_of_charge()}',
#        'battery_temp_C' : f'{controller.get_battery_temperature()}',
#        'remote_battery_temp_C' : f'{controller.get_remote_battery_temperature()}'
#        'controller_temp_C' : f'{controller.get_controller_temperature()}',
#        'battery_status' : f'{controller.get_battery_status()}',
#        'charging_equipment_status' : f'{controller.get_charging_equipment_status()}',
#        'discharging_equipment_status' : f'{controller.get_discharging_equipment_status()}'
#        'day_time' : f'{controller.is_day()}',
#        'night_time' : f'{controller.is_night()}',
#        'max_batt_voltage_today_V' : f'{controller.get_maximum_battery_voltage_today()}'
#        'min_batt_voltage_today_V' : f'{controller.get_minimum_battery_voltage_today()}'
#        'max_pv_voltage_today_V' : f'{controller.get_maximum_pv_voltage_today()}',
#        'min_pv_voltage_today_V' : f'{controller.get_minimum_pv_voltage_today()}',
#        'device_overtemp_status' : f'controller.is_device_over_temperature()}',
#        'energy_consumed_today_kWh' : f'controller.get_consumed_energy_today()}',
#        'energy_consumed_this_month_kWh' : f'{controller.get_consumed_energy_this_month()}',
#        'energy_consumed_this_year_kWh' : f'{controller.get_consumed_energy_this_year()}',
#        'energy_consumed_total_kWh' : f'{controller.get_total_consumed_energy()}',
#        'energy_generated_today_kWh' : f'{controller.get_generated_energy_today()}',
#        'energy_generated_this_month_kWh' : f'{controller.get_generated_energy_this_month()}',
#        'energy_generated_this_year_kWh' : f'{controller.get_generated_energy_this_year()}',
#        'energy_generated_total_kWh' : f'{controller.get_total_generated_energy()}',
#        'current_device_time' : f'{controller.get_rtc()}',
#        #Battery Parameters:
#        'rated_charging_current_A' : f'{controller.get_rated_charging_current()}',
#        'rated_load_current_A' : f'{controller.get_rated_load_current()}',
#        'battery_real_rated_voltage_V' : f'{controller.get_battery_real_rated_voltage()}',
#        'battery_type' : f'{controller.get_battery_type()}',
#        'battery_capacity_AH' : f'{controller.get_battery_capacity()}',
#        'temperature_compensation_coefficient_mV/C/Cell' : f'{controller.get_temperature_compensation_coefficient()}',
#        'over_voltage_disconnect_voltage_V' : f'{controller.get_over_voltage_disconnect_voltage()}V',
#        'charging_limit_voltage_V' : f'{controller.get_charging_limit_voltage()}',
#        'over_voltage_reconnect_voltage_V' : f'{controller.get_over_voltage_reconnect_voltage()}'
#        'equalize_charging_voltage_V' : f'{controller.get_equalize_charging_voltage()}',
#        'boost_charging_voltage_V' : f'{controller.get_boost_charging_voltage()}',
#        'float_charging_voltage_V' : f'{controller.get_float_charging_voltage()}',
#        'boost_reconnect_charging_voltage_V' : f'{controller.get_boost_reconnect_charging_voltage()}',
#        'low_voltage_reconnect_voltage_V' : f'{controller.get_low_voltage_reconnect_voltage()}',
#        'under_voltage_recover_voltage_V' : f'{controller.get_under_voltage_recover_voltage()}',
#        'under_voltage_warning_voltage_V' : f'{controller.get_under_voltage_warning_voltage()}',
#        'low_voltage_disconnect_voltage_V' : f'{controller.get_low_voltage_disconnect_voltage()}V',
#        'discharge_limit_voltage_V' : f'{controller.get_discharging_limit_voltage()}',
#        'battery_rated_voltage_V' : f'{controller.get_battery_rated_voltage()}',
#        'default_load_on/off_in_manual_mode' : f'{controller.get_default_load_on_off_in_manual_mode()}',
#        'equalize_duration_min' : f'{controller.get_equalize_duration()}',
#        'boost_duration_min' : f'{controller.get_boost_duration()}',
#        'battery_discharge_%' : f'{controller.get_battery_discharge()}',
#        'battery_charge_%' : f'{controller.get_battery_charge()}',
#        'charging_mode' : f'{controller.get_charging_mode()}'
#}
