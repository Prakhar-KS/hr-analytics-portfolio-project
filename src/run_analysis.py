import pandas as pd
import sqlite3
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

def get_sql_server_engine():
    from src.load_to_sql import setup_env
    server, driver = setup_env()
    if not server:
        return None
    db_name = "HRAnalytics"
    params = urllib.parse.quote_plus(f"DRIVER={{{driver}}};SERVER={server};DATABASE={db_name};Trusted_Connection=yes;")
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    try:
        with engine.connect() as conn:
            pass
        return engine
    except Exception:
        logger.warning("Could not connect to HRAnalytics. Falling back.")
        return None

def get_sqlite_fallback(clean_dir):
    logger.info("Setting up SQLite fallback in-memory database...")
    conn = sqlite3.connect(':memory:')
    tables = ['departments', 'job_roles', 'employees', 'compensation', 'satisfaction']
    for table in tables:
        df = pd.read_csv(clean_dir / f"{table}.csv")
        df.to_sql(table, conn, index=False)
    return conn

def split_queries(sql_text):
    # Split by double newline followed by -- Business Question
    queries = []
    current_q = []
    for line in sql_text.split('\n'):
        if line.startswith('-- Business Question') and current_q:
            queries.append('\n'.join(current_q))
            current_q = [line]
        else:
            current_q.append(line)
    if current_q:
        queries.append('\n'.join(current_q))
    return [q.strip() for q in queries if q.strip()]

def main():
    root_dir = Path(__file__).parent.parent
    clean_dir = root_dir / 'data' / 'clean'
    sql_path = root_dir / 'sql' / 'advanced_analysis.sql'
    out_dir = root_dir / 'docs'
    out_dir.mkdir(parents=True, exist_ok=True)
    
    with open(sql_path, 'r') as f:
        sql_text = f.read()
        
    queries = split_queries(sql_text)
    
    engine = get_sql_server_engine()
    fallback_conn = None
    
    if not engine:
        logger.warning("Falling back to SQLite with pandas.")
        fallback_conn = get_sqlite_fallback(clean_dir)
        
    for i, query in enumerate(queries):
        q_num = i + 1
        logger.info(f"Executing Q{q_num}...")
        try:
            if engine:
                with engine.connect() as conn:
                    df = pd.read_sql(sqlalchemy.text(query), conn)
            else:
                df = pd.read_sql(query, fallback_conn)
                
            print(f"\n--- Q{q_num} Results ---")
            print(df.head())
            df.to_csv(out_dir / f'query_results_q{q_num}.csv', index=False)
            logger.info(f"Saved Q{q_num} results.")
        except Exception as e:
            logger.error(f"Error executing Q{q_num}: {e}")
            
    if fallback_conn:
        fallback_conn.close()

if __name__ == "__main__":
    main()
