import os
import psycopg2
import logging


def create_postgres_connection():
    """Create a connection to PostgreSQL."""
    try:
        # Read PostgreSQL connection details from environment variables
        postgres_host = os.getenv("POSTGRES_HOST")
        postgres_port = os.getenv("POSTGRES_PORT")
        postgres_db = os.getenv("POSTGRES_DB")
        postgres_user = os.getenv("POSTGRES_USER")
        postgres_password = os.getenv("POSTGRES_PASSWORD")
        
        print({ 
                'postgres_host' : postgres_host, 
                'postgres_port': postgres_port ,
                'postgres_db': postgres_db, 
                'postgres_user': postgres_user, 
                'postgres_password': postgres_password })
        # Check if all required environment variables are present
        if not all([postgres_host, postgres_port, postgres_db, postgres_user, postgres_password]):
            raise ValueError("Missing PostgreSQL environment variables")
        
        # Construct the connection string
        conn_str = f"dbname={postgres_db} user={postgres_user} password={postgres_password} host={postgres_host} port={postgres_port}"
        
        # Establish connection to PostgreSQL
        conn = psycopg2.connect(conn_str)
        return conn
    except psycopg2.Error as e:
        logging.error(f"Error occurred while connecting to PostgreSQL: {e}")
        return None
    except ValueError as ve:
        logging.error(f"Missing environment variables: {ve}")
        return None