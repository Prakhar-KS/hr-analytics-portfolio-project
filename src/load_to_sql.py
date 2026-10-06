import pandas as pd
import pyodbc
import sqlalchemy
from sqlalchemy import create_engine
import urllib
from dotenv import load_dotenv
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_odbc_driver():
    drivers = [driver for driver in pyodbc.drivers() if 'SQL Server' in driver]
    if not drivers:
        logger.warning("No ODBC Driver for SQL Server found.")
        return None
    # Prefer ODBC Driver 17 or 18
    for d in drivers:
        if 'ODBC Driver 17' in d or 'ODBC Driver 18' in d:
            return d
    return drivers[0]

def test_connection(server, driver):
    conn_str = f"DRIVER={{{driver}}};SERVER={server};Trusted_Connection=yes;"
    try:
        conn = pyodbc.connect(conn_str, timeout=3)
        conn.close()
        return True
    except Exception as e:
        return False

def setup_env():
    load_dotenv()
    
    servers_to_try = [
        os.getenv('SQL_SERVER'), 
        r"localhost\SQLEXPRESS", 
        "localhost", 
        r"(localdb)\MSSQLLocalDB"
    ]
    
    driver = find_odbc_driver()
    if not driver:
        return None, None
        
    for server in servers_to_try:
        if server and test_connection(server, driver):
            logger.info(f"Successfully connected to SQL Server at {server} with {driver}")
            return server, driver
            
    logger.warning("Could not connect to any SQL Server instance.")
    return None, None

def run_schema(engine, schema_path):
    with open(schema_path, 'r') as f:
        sql = f.read()
    
    commands = sql.split('GO')
    with engine.begin() as conn:
        for cmd in commands:
            if cmd.strip():
                conn.execute(sqlalchemy.text(cmd))
    logger.info("Schema successfully executed.")

def load_data(engine, clean_dir):
    tables = ['departments', 'job_roles', 'employees', 'compensation', 'satisfaction']
    
    for table in tables:
        df = pd.read_csv(clean_dir / f"{table}.csv")
        logger.info(f"Loading {len(df)} rows into {table}...")
        df.to_sql(table, con=engine, if_exists='append', index=False, chunksize=500, method='multi')
        
        # Verify row counts
        with engine.connect() as conn:
            res = conn.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM {table}")).fetchone()
            assert res[0] == len(df), f"Row count mismatch for {table}"
        logger.info(f"Verified {table} loaded {res[0]} rows.")

def main():
    root_dir = Path(__file__).parent.parent
    clean_dir = root_dir / 'data' / 'clean'
    schema_path = root_dir / 'sql' / 'schema.sql'
    
    server, driver = setup_env()
    if not server:
        logger.warning("Skipping SQL Server load (could not connect). Proceeding to fallback mode later.")
        return
        
    db_name = "HRAnalytics"
    
    # Create DB first (can't do it inside transaction)
    conn_str = f"DRIVER={{{driver}}};SERVER={server};Trusted_Connection=yes;autocommit=True"
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(f"IF DB_ID('{db_name}') IS NULL CREATE DATABASE {db_name}")
        cursor.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error creating DB: {e}")
        return

    # Now connect with SQLAlchemy to the database
    params = urllib.parse.quote_plus(f"DRIVER={{{driver}}};SERVER={server};DATABASE={db_name};Trusted_Connection=yes;")
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)
    
    try:
        run_schema(engine, schema_path)
        load_data(engine, clean_dir)
    except Exception as e:
        logger.error(f"Error during load: {e}")

if __name__ == "__main__":
    main()
