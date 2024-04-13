from datetime import datetime, timedelta, date
from io import BytesIO

import os
import pandas as pd
import psycopg2
from airflow.decorators import dag, task
from postgres_connection import create_postgres_connection
from minio import Minio
from minio.error import S3Error

default_args = {
    'owner' : 'harshal',
    'retries' : 2,
    'retry_delay' : timedelta(minutes=2)
}

@task
def read_data_from_postgres():
    """
    Fetches data from PostgreSQL database.
        
    Returns:
        pandas.DataFrame: DataFrame containing fetched data.
    """
    try:
        # Connect to PostgreSQL
        conn = create_postgres_connection()
        
        # Read data from PostgreSQL into a DataFrame
        query = f"SELECT * FROM {os.getenv('POSTGRES_SCHEMA')}.{os.getenv('POSTGRES_TABLE')} WHERE DATE_TRUNC('day', api_call_timestamp) = CURRENT_DATE"
        df = pd.read_sql(query, conn)
        
        # Close connection
        conn.close()

        print("Data fetched successfully!")
        return df
    except psycopg2.Error as e:
        print(f"Error occurred during database operation: {e}")
        return None

@task
def db_to_bucket(df: list):
    """
    Uploads DataFrame to MinIO bucket.
    
    Args:
        df (pandas.DataFrame): DataFrame to be uploaded.
    """
    try:

        object_name = f"weather_records_{date.today().strftime('%Y%m%d')}.csv"
        csv = df.to_csv(index=False).encode("utf-8")

        # Initialize MinIO client
        minio_client = Minio(
            endpoint=os.getenv('MINIO_HOST'),
            access_key=os.getenv('MINIO_ACCESS_KEY'),
            secret_key=os.getenv('MINIO_SECRET_KEY'),
            secure=False
        )
        bucket_name = os.getenv('MINIO_BUCKET_NAME')

        found = minio_client.bucket_exists(bucket_name)
        if not found:
            minio_client.make_bucket(bucket_name)
        else:
            print(f"Bucket '{bucket_name}' already exists!")

        minio_client.put_object(
            bucket_name, object_name, data=BytesIO(csv), length=len(csv), content_type="application/csv"
        )

        print(f"File uploaded successfully to MinIO bucket.")

    except S3Error as err:
        print(f"Error occurred: {err}")   

@dag(
    dag_id = 'db_to_bucket',
    default_args=default_args,
    description = 'This DAG orchestrates the movement of data from postgres database to minio bucket.',
    schedule_interval='55 23 * * *',
    start_date=datetime(2024,4,10),
    catchup=False,
)
def api_to_db_load():

    df = read_data_from_postgres()
    db_to_bucket(df)
    
task2 = api_to_db_load()