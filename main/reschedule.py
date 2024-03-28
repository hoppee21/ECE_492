import sqlite3
import pandas as pd
import time
from datetime import datetime


# Function to round down timestamps to the nearest minute
def round_down_time(dt_str):
    # Convert string to a datetime object
    dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f')
    # Round down to the nearest minute
    return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)


# Connect to your source and main databases
source_conn = sqlite3.connect('/var/www/data.db')
main_conn = sqlite3.connect('/var/www/main.db')

source_cursor = source_conn.cursor()
main_cursor = main_conn.cursor()
main_cursor.execute("CREATE TABLE IF NOT EXISTS TEMP (T FLOAT,Arrive_time TIME)")
main_cursor.execute("CREATE TABLE IF NOT EXISTS HUMIDITY (H FLOAT,Arrive_time TIME)")
main_cursor.execute("CREATE TABLE IF NOT EXISTS OCCUPANCY (O INT,Arrive_time TIME)")

while True:
    # Read data from source database for a specific table, e.g., Temp
    source_cursor.execute("SELECT * FROM TEMP")
    query = "SELECT * FROM TEMP"
    df_temp = pd.read_sql_query(query, source_conn)

    # remove the data that has been collect from TEMP
    source_conn.execute("DELETE FROM TEMP")

    # Convert Arrive_time to rounded-down timestamps
    df_temp['Arrive_time'] = df_temp['Arrive_time'].apply(round_down_time)
    df_aggregated = df_temp.groupby('Arrive_time').mean().reset_index()
    # round the number to two decimals
    df_aggregated = df_aggregated.round(2)
    df_aggregated.to_sql('T EMP', main_conn, if_exists='append', index=False)

    # Read data from source database for a specific table, e.g., Temp
    source_cursor.execute("SELECT * FROM OCCUPANCY")
    query = "SELECT * FROM OCCUPANCY"
    df_temp = pd.read_sql_query(query, source_conn)

    source_conn.execute("DELETE FROM OCCUPANCY")

    # Convert Arrive_time to rounded-down timestamps
    df_temp['Arrive_time'] = df_temp['Arrive_time'].apply(round_down_time)
    df_aggregated = df_temp.groupby('Arrive_time').max().reset_index()
    # round the number to two decimals
    df_aggregated = df_aggregated.round(2)
    df_aggregated.to_sql('OCCUPANCY', main_conn, if_exists='append', index=False)

    # Read data from source database for a specific table, e.g., Temp
    source_cursor.execute("SELECT * FROM HUMIDITY")
    query = "SELECT * FROM HUMIDITY"
    df_temp = pd.read_sql_query(query, source_conn)

    source_conn.execute("DELETE FROM HUMIDITY")

    # Convert Arrive_time to rounded-down timestamps
    df_temp['Arrive_time'] = df_temp['Arrive_time'].apply(round_down_time)
    df_aggregated = df_temp.groupby('Arrive_time').mean().reset_index()
    # round the number to two decimals
    df_aggregated = df_aggregated.round(2)
    df_aggregated.to_sql('HUMIDITY', main_conn, if_exists='append', index=False)

    time.sleep(10 * 60)
