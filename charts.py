import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('/home/stu/battery.db')
cur = conn.cursor()

cols_df = pd.read_sql_query('PRAGMA table_info(battery)',conn)

columns = cols_df['name'].tolist()
print(columns)
#'datetime', 'solar_voltage_V', 'solar_current_A', 'solar_power_W', 'load_voltage_V', 'load_current_A', 'load_power_W', 'battery_voltage_V', 'battery_current_A', 'battery_power_W', 'battery_soc_%']

status_df = pd.read_sql_query('SELECT * FROM status',conn)
telemetry_df = pd.read_sql_query('SELECT * FROM battery',conn)

