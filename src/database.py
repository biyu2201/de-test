import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
import pandas as pd
import logging

DB = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")

# Create engine at module level for connection pooling
engine_string = f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'

try:
    engine: Engine = create_engine(engine_string, pool_pre_ping=True)
except Exception as e:
    logging.warning(f"Could not create database engine.")
    engine = None


def load_to_pg(df: pd.DataFrame, table_name: str, insert_method: str = "append"):   
    try:
        with engine.begin() as connection:
            df.to_sql(
                table_name,
                con=connection,
                if_exists=insert_method,
                index=False
            )
        logging.info(f"Successfully loaded {len(df)} rows to {table_name}.")
    except Exception as e:
        logging.error(f"Failed to load data to PostgreSQL: {e}")
        raise