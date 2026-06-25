import sys
import time
from datetime import datetime, timezone, timedelta
import mariadb
from epevermodbus.driver import EpeverChargeController
import logging

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('tacoma_data_logger.log')
stream_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p'))
file_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p'))
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

try:
    controller = EpeverChargeController('/dev/tacomachargecontroller',1)
except Exception as e:
    logger.info(f'Error: {e}. USB serial device may not found...exiting.')
    exit()

try:
    unix_time = int(datetime.now().timestamp())
    #Convert to UTC time:
    date_time = datetime.now()+timedelta(hours=7, minutes=0)
    data = {
        'unix_time ': unix_time,
        'date_time ' : date_time,
        #Stats:
        'solar_voltage_V ' : f'{controller.get_solar_voltage()}',
        'solar_current_A ' : f'{controller.get_solar_current()}',
        'solar_power_W ' : f'{controller.get_solar_power()}',
        'load_voltage_V ' : f'{controller.get_load_voltage()}',
        'load_current_A ' : f'{controller.get_load_current()}',
        'load_power_W ' : f'{controller.get_load_power()}',
        'battery_voltage_V ' : f'{controller.get_battery_voltage()}',
        'battery_current_A ' : f'{controller.get_battery_current()}',
        'battery_power_W ' : f'{controller.get_battery_power()}',
        'battery_soc_percent ' : f'{controller.get_battery_state_of_charge()}'
    }

    battery_status = controller.get_battery_status()
    charging_equipment_status = controller.get_charging_equipment_status()
    equip_data = {
        'unix_time': unix_time,
        'date_time': date_time,
    #    'current_device_time ' : f'{controller.get_rtc()}',
        #Battery Status
        'device_overtemp_status' : f'{controller.is_device_over_temperature()}',
        'wrong_id_for_rated_voltage' : battery_status['wrong_identifaction_for_rated_voltage'],
        'battery_inner_resistance_abnormal' : battery_status['battery_inner_resistence_abnormal'],
        'temperature_warning_status' : battery_status['temperature_warning_status'],
        'battery_status' : battery_status['battery_status'],
        #Charging Equipment Status
        'input_voltage_status' : charging_equipment_status['input_voltage_status'],
        'charging_mosfet_is_short_circuit' : charging_equipment_status['charging_mosfet_is_short_circuit'],
        'charging_or_anti_reverse_mosfet_is_open_circuit' : charging_equipment_status['charging_or_anti_reverse_mosfet_is_open_circuit'],
        'anti_reverse_mosfet_is_short_circuit' : charging_equipment_status['anti_reverse_mosfet_is_short_circuit'],
        'input_over_current' : charging_equipment_status['input_over_current'],
        'load_short_circuit' : charging_equipment_status['load_short_circuit'],
        'load_mosfet_short_circuit' : charging_equipment_status['load_mosfet_short_circuit'],
        'disequilibrium_in_three_circuits': charging_equipment_status['disequilibrium_in_three_circuits'],
        'pv_input_short_circuit' : charging_equipment_status['pv_input_short_circuit'],
        'charging_status' : charging_equipment_status['charging_status'],
        'fault' : charging_equipment_status['fault'],
        'running' : charging_equipment_status['running']
    }

except Exception as e:
    logger.info(f'Problem reading battery data into dict: {e}')
    exit() 

try:
    data_tuple = tuple(list(data.values()))
    equip_data_tuple = tuple(list(equip_data.values()))

    connection_params = {
            'user' : 'stu',
            'password' : 'kukaww',
            'host' : 'localhost',
            'database' : 'tacoma_grid'
            }
    connection = mariadb.connect(**connection_params)
    cursor = connection.cursor()
    cursor.execute('SHOW TABLES;')
    result = cursor.fetchall()
    tables = [x[0] for x in result]
    if 'battery' not in tables:
        cursor.execute(f'CREATE TABLE battery (unix_time INT, date_time TIMESTAMP, solar_voltage_V FLOAT, solar_current_A FLOAT, solar_power_W FLOAT, load_voltage_V FLOAT, load_current_A FLOAT, load_power_W FLOAT, battery_voltage_V FLOAT, battery_current_A FLOAT, battery_power_W FLOAT, battery_soc_percent INT)')
        
    if 'status' not in tables:
        cursor.execute(f'CREATE TABLE status (unix_time INT, date_time TIMESTAMP, device_overtemp_status TEXT, wrong_id_for_rated_voltage TINYINT, battery_inner_resistance_abnormal TINYINT, temperature_warning_status TEXT, battery_status TEXT, input_voltage_status TEXT, charging_mosfet_is_short_circuit TINYINT, charging_or_anti_reverse_mosfet_is_open_circuit TINYINT, anti_reverse_mosfet_is_short_circuit TINYINT, input_over_current TINYINT, load_short_circuit TINYINT, load_mosfet_short_circuit TINYINT, disequilibrium_in_three_circuits TINYINT, pv_input_short_circuit TINYINT, charging_status TEXT, fault TINYINT, running TINYINT)')
        
   
    placeholders = '(' + "".join('?,' * len(data_tuple))[:-1] + ')'
    cursor.execute(f'INSERT INTO battery VALUES {placeholders}',data_tuple)

    placeholders = '(' + "".join('?,' * len(equip_data_tuple))[:-1] + ')'
    cursor.execute(f'INSERT INTO status VALUES {placeholders}',equip_data_tuple)

    connection.commit()
    connection.close()
    logger.info(f'DB entry successful')
except Exception as e:
    logger.info(f'Problem inserting data into database: {e}')
