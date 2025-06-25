import os
import logging
from datetime import datetime
from src.etl.extractor import csv_extractor
from src.etl.api_extractor import api_extractor, API_LOAD_ORDER
from src.etl.transformer import transformer
from src.etl.loader import postgres_loader

# Setup professional logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
ETL_LOG_FILE = os.path.join(LOG_DIR, f"etl_pipeline_{datetime.now():%Y-%m-%d_%H-%M-%S}.log")
logging.basicConfig(
    filename=ETL_LOG_FILE,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Define CSV table load order for foreign key compliance
CSV_LOAD_ORDER = [
    "stg_pro_count__areatb", "stg_pro_count__batterytb", "stg_pro_count__divisiontb",
    "stg_pro_count__fieldgrouptb", "stg_pro_count__producingmethodstb",
    "stg_pro_count__producingstatustb", "stg_pro_count__routetb",
    "stg_pro_count__statecountynamestb", "stg_aries__ac_property",
    "stg_pro_count__completiontb"
]

def run_csv_pipeline(all_data):
    """Runs the idempotent ETL process for all CSV files."""
    print("\n========== CSV PIPELINE STARTED ==========")
    logging.info("CSV Pipeline Started")
    for table_name in CSV_LOAD_ORDER:
        if table_name not in all_data: continue
        print(f"\n[PROCESS] Loading CSV table: {table_name}")
        df = all_data[table_name]
        df = transformer.clean_column_names(df)
        if table_name == "stg_pro_count__completiontb":
            df = transformer.transform_completion_data(df)
        postgres_loader.truncate_table(table_name)
        postgres_loader.load_dataframe(df, table_name)
    print("========== CSV PIPELINE COMPLETED ==========")
    logging.info("CSV Pipeline Completed")

def run_api_pipeline(all_data):
    """Runs the idempotent ETL process for all API endpoints."""
    print("\n========== API PIPELINE STARTED ==========")
    logging.info("API Pipeline Started")
    for table_name in API_LOAD_ORDER:
        if table_name not in all_data: continue
        print(f"\n[PROCESS] Loading API table: {table_name}")
        df = all_data[table_name]
        df = transformer.clean_column_names(df)
        
        # Professional Solution: Use a smaller batch size for the table
        # with large text fields to avoid potential network/SSL buffer issues.
        batch_size = 500 if table_name == "stg_wiserock__note" else 5000
        print(f"    > Using batch size: {batch_size}")
        
        postgres_loader.truncate_table(table_name)
        postgres_loader.load_dataframe(df, table_name, batch_size=batch_size)
        
    print("========== API PIPELINE COMPLETED ==========")
    logging.info("API Pipeline Completed")

def main():
    """Main entry point for the ETL application."""
    print("=" * 60)
    print(f"              ETL PIPELINE EXECUTION STARTED at {datetime.now()}")
    print("=" * 60)
    logging.info("ETL Pipeline Execution Started")

    try:
        # Extract all data first to control the load order
        print("--- Extracting CSV data...")
        csv_data = csv_extractor.extract_all()
        print("--- Extracting API data...")
        api_data = api_extractor.extract_all()
        
        #run_csv_pipeline(csv_data)
        run_api_pipeline(api_data)
        
        logging.info("ETL Pipeline Execution Finished Successfully")
    except Exception as error:
        logging.error(f"ETL pipeline failed: {error}", exc_info=True)
        print(f"[FATAL ERROR] ETL pipeline failed: {error}")
        raise

    print("=" * 60)
    print(f"              ETL PIPELINE EXECUTION FINISHED at {datetime.now()}")
    print("=" * 60)

if __name__ == "__main__":
    main()
