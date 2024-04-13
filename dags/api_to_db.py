from datetime import datetime,timedelta

import os
import requests
from airflow.decorators import dag,task
from postgres_connection import create_postgres_connection

default_args = {
    'owner' : 'harshal',
    'retries' : 2,
    'retry_delay' : timedelta(minutes=2)
}

@task
def fetch_weather_data(api_key, city):
    """
    Task to fetch weather data from the WeatherAPI.
    """
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

@task
def parse_json(json_data):
    """
    Task to parse the fetched JSON weather data.
    """
    return json_data['location'], json_data['current']

@task
def create_schema_if_not_exists():
    """
    Task to create the PostgreSQL schema if it does not exist.
    """
    conn = create_postgres_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('POSTGRES_SCHEMA')}")
        conn.commit()
        print("Schema created successfully!")
    except Exception as e:
        print(f"Error occurred during schema creation: {e}")
        conn.rollback()
    finally:
        conn.close()

@task
def create_table_if_not_exists():
    """
    Task to create the PostgreSQL table if it does not exist.
    """
    conn = create_postgres_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {os.getenv('POSTGRES_SCHEMA')}.{os.getenv('POSTGRES_TABLE')} (
                    city_name VARCHAR(60),
                    region VARCHAR(120),
                    country VARCHAR(60),
                    local_time TIMESTAMP,
                    temp_c DECIMAL(10, 2),
                    temp_f DECIMAL(10, 2),
                    condition VARCHAR(120),
                    wind_mph DECIMAL(10, 2),
                    wind_kph DECIMAL(10, 2),
                    wind_degree DECIMAL(10, 2),
                    wind_dir VARCHAR(20),
                    pressure_mb DECIMAL(10, 2),
                    pressure_in DECIMAL(10, 2),
                    precip_mm DECIMAL(10, 2),
                    precip_in DECIMAL(10, 2),
                    humidity INT,
                    cloud INT,
                    feelslike_c DECIMAL(10, 2),
                    feelslike_f DECIMAL(10, 2),
                    vis_km DECIMAL(10, 2),
                    vis_miles DECIMAL(10, 2),
                    uv DECIMAL(10, 2),
                    gust_mph DECIMAL(10, 2),
                    gust_kph DECIMAL(10, 2),
                    api_call_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
        print("Table created successfully!")
    except Exception as e:
        print(f"Error occurred during table creation: {e}")
        conn.rollback()
    finally:
        conn.close()

@task
def insert_into_postgres(data):
    location, current = data
    conn = create_postgres_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            INSERT INTO {os.getenv('POSTGRES_SCHEMA')}.{os.getenv('POSTGRES_TABLE')} (city_name, region, country, local_time, temp_c, temp_f, condition, wind_mph, wind_kph, wind_degree, wind_dir, pressure_mb, pressure_in, precip_mm, precip_in, humidity, cloud, feelslike_c, feelslike_f, vis_km, vis_miles, uv, gust_mph, gust_kph, api_call_timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"""
        , (
                location['name'],
                location['region'],
                location['country'],
                location['localtime'],
                current['temp_c'],
                current['temp_f'],
                current['condition']['text'],
                current['wind_mph'],
                current['wind_kph'],
                current['wind_degree'],
                current['wind_dir'],
                current['pressure_mb'],
                current['pressure_in'],
                current['precip_mm'],
                current['precip_in'],
                current['humidity'],
                current['cloud'],
                current['feelslike_c'],
                current['feelslike_f'],
                current['vis_km'],
                current['vis_miles'],
                current['uv'],
                current['gust_mph'],
                current['gust_kph']
            ))
        conn.commit()
        print("Data inserted successfully!")
    except Exception as e:
        print(f"Error occurred during insert operation: {e}")
        conn.rollback()
    finally:
        conn.close()  

@dag(
    dag_id = 'api_to_db',
    default_args=default_args,
    description = 'This DAG orchestrates the movement of data from a weather api to postgres database.',
    schedule_interval='@hourly',
    start_date=datetime(2024,4,10),
    catchup=False,
)
def api_to_db_load():
    
    api_key = os.getenv("API_KEY")
    city = os.getenv("API_LOCATION")

    create_schema_task = create_schema_if_not_exists()
    create_table_task = create_table_if_not_exists()

    create_table_task.set_upstream(create_schema_task)
    
    weather_data = fetch_weather_data(api_key, city)
    parsed_data = parse_json(weather_data)
    insert_into_postgres(parsed_data)
    
task1 = api_to_db_load()
    
