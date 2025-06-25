import pandas as pd
import time
import logging
from sqlalchemy.engine import Engine
from sqlalchemy import text
from psycopg2.extras import execute_values
from src.database import engine
from src.config import settings

# Configure logger for batch errors
logger = logging.getLogger("loader")
logger.setLevel(logging.ERROR)
# Use 'a' for append mode so logs from multiple runs are kept.
file_handler = logging.FileHandler("logs/failed_batches.log", mode='a')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
if not logger.handlers:
    logger.addHandler(file_handler)

class PostgresLoader:
    """
    A robust, production-grade PostgreSQL loader.
    - Uses a single connection per table load for efficiency.
    - Implements automatic retries for transient network errors.
    - Supports `ON CONFLICT DO NOTHING` for idempotent writes.
    """
    def __init__(self, engine: Engine, schema: str):
        self.engine = engine
        self.schema = schema

    def truncate_table(self, table_name: str):
        """Clears all data from a table to ensure a clean slate."""
        print(f"--> Truncating table: {self.schema}.{table_name}")
        try:
            # The connection.execution_options is crucial for TRUNCATE
            # as it cannot run inside a transaction block in some PostgreSQL versions.
            with self.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
                query = text(f'TRUNCATE TABLE "{self.schema}"."{table_name}" RESTART IDENTITY CASCADE;')
                connection.execute(query)
            print(f"--> Successfully truncated {table_name}.")
        except Exception as e:
            print(f"[ERROR] Failed to truncate {table_name}: {e}")
            raise

    def load_dataframe(self, df: pd.DataFrame, table_name: str, batch_size: int = 5000, retries: int = 3):
        """
        Loads a DataFrame into a PostgreSQL table with a single connection and retries.
        """
        if df.empty:
            print(f"[SKIP] No data to load for table: {table_name}")
            return

        columns = [f'"{col}"' for col in df.columns]
        total_rows = len(df)
        num_batches = (total_rows + batch_size - 1) // batch_size

        print(f"--> Loading {total_rows} rows into {self.schema}.{table_name} in {num_batches} batches")

        # Use a single connection for the entire table load for efficiency and stability.
        with self.engine.connect() as connection:
            for i in range(0, total_rows, batch_size):
                batch_df = df.iloc[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                
                # --- Retry Logic ---
                for attempt in range(retries):
                    try:
                        # Use a nested transaction for the batch insert.
                        with connection.begin():
                            values = [tuple(row) for row in batch_df.itertuples(index=False, name=None)]
                            
                            # Use execute_values from psycopg2 for high performance
                            raw_conn = connection.connection
                            with raw_conn.cursor() as cursor:
                                sql = f"""
                                    INSERT INTO "{self.schema}"."{table_name}" ({', '.join(columns)})
                                    VALUES %s
                                    ON CONFLICT DO NOTHING
                                """
                                execute_values(cursor, sql, values)
                        
                        print(f"    > Batch {batch_num}/{num_batches} committed successfully.")
                        break # Success, exit the retry loop.

                    except Exception as e:
                        print(f"    > Batch {batch_num} Attempt {attempt + 1}/{retries} failed: {e}")
                        logger.error(f"Batch {batch_num} (Table: {table_name}) Attempt {attempt + 1} failed: {e}")
                        if attempt < retries - 1:
                            time.sleep(2) # Wait for 2 seconds before retrying
                        else:
                            print(f"    > CRITICAL: Batch {batch_num} failed after {retries} attempts. See logs.")
                            
        print(f"--> Finished loading {table_name}")


# Global instance for reuse
postgres_loader = PostgresLoader(engine=engine, schema=settings.DB_SCHEMA)
