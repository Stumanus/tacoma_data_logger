import sys
import time
from datetime import datetime
import sqlite3
from epevermodbus.driver import EpeverChargeController
import logging

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('tacoma_data_logger.log')
stream_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p'))
file_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p'))
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

'''Add some retry logic to deal with situations where the comm cable becomes disconnected and then plugged back in so
the whole program doesn't hang'''

try:
    controller = EpeverChargeController('/dev/tacomachargecontroller',1)
except Exception as e:
    logger.info(f'Error: {e}. Problem initializing connection with charge controller...exiting.')
    exit()

try:
    data = {
        'unix_time': int(datetime.now().timestamp()),
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
        'battery_soc_%' : f'{controller.get_battery_state_of_charge()}'
    }
    battery_status = controller.get_battery_status()
    equip_data = {
        'unix_time': int(datetime.now().timestamp()),
        'current_device_time' : f'{controller.get_rtc()}',
        'device_overtemp_status' : f'{controller.is_device_over_temperature()}',
        #Battery Status
        'wrong_id_for_rated_voltage' : battery_status['wrong_identifaction_for_rated_voltage'],
        'battery_inner_resistance_abnormal' : battery_status['battery_inner_resistence_abnormal'],
        'temperature_warning_status' : battery_status['temperature_warning_status'],
        'battery_status' : battery_status['battery_status']
    }
except Exception as e:
    logger.info(f'Problem reading battery data into dict: {e}')

try:
    data_tuple = tuple(list(data.values()))
    column_tuple = tuple(list(data.keys()))

    equip_data_tuple = tuple(list(equip_data.values()))
    equip_column_tuple = tuple(list(equip_data.keys()))

    conn = sqlite3.connect('/home/stu/tacoma_data_logger/battery.db')
    cur = conn.cursor()

    tables = [x[0] for x in cur.execute('SELECT name FROM sqlite_master').fetchall()]
    if 'battery' not in tables:
        cur.execute(f'CREATE TABLE battery{column_tuple}')
    if 'status' not in tables:
        cur.execute(f'CREATE TABLE status{equip_column_tuple}')

    placeholders = ('?, ' * len(data_tuple))[:-2]
    cur.execute(f'INSERT INTO battery VALUES({placeholders})',data_tuple)

    placeholders = ('?, ' * len(equip_data))[:-2]
    cur.execute(f'INSERT INTO status VALUES({placeholders})',equip_data_tuple)

    conn.commit()
    conn.close()
    logger.info(f'DB entry successful')
except Exception as e:
    logger.info(f'Problem inserting data into database: {e}')

