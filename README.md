Analytics Engineer Technical Assessment - ETL Pipeline
This project contains a professional-grade ETL (Extract, Transform, Load) pipeline built with Python. It is designed to ingest data from two distinct sources—a set of local CSV files and a paginated web API—and load it into a PostgreSQL database.

The framework is designed to be robust, extensible, and maintainable, following industry best practices for data engineering.

Project Architecture
This solution is built as a modular framework, not a simple script. Each component has a single, clear responsibility, making the system easy to understand, test, and extend in the future.

main.py: The main entry point and orchestrator for the entire ETL process. It controls the high-level flow, calling the CSV and API pipelines in the correct sequence.

src/config.py: A centralized configuration module. It securely loads all necessary settings (database credentials, API keys, file paths) from an external .env file, ensuring no sensitive information is hardcoded in the application logic.

src/database.py: Handles the creation of the database connection engine using SQLAlchemy. This isolates all database connection logic into a single, reusable component.

src/etl/: A dedicated package for the core ETL logic, separated by function:

extractor.py: Contains the CsvExtractor class, responsible for finding and reading all source CSV files from the /data directory.

api_extractor.py: Contains the ApiExtractor class, which handles the complexities of the web API, including token-based authentication and a robust pagination loop to fetch all records.

transformer.py: Contains the Transformer class. This component is responsible for all data cleaning and standardization, such as correcting data types (activeflag) and ensuring consistent column naming.

loader.py: Contains the PostgresLoader class. This component is responsible for loading data into the PostgreSQL database. It is designed to be resilient, using a single connection per table load and implementing automatic retries to handle transient network errors.

alembic/: This directory contains the database migration scripts managed by Alembic. This allows for version-controlled, repeatable, and programmatic setup of the database schema.

logs/: This directory is automatically created to store detailed log files for each pipeline run, providing a clear audit trail.

Setup and Execution
To set up and run this project, follow these steps.

1. Prerequisites
Python 3.10+

Access to a PostgreSQL database

2. Installation
First, clone the repository and navigate into the project directory.

It is highly recommended to use a Python virtual environment to manage dependencies.

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

Install all required Python packages using the requirements.txt file:

pip install -r requirements.txt

3. Configuration
The pipeline requires credentials for both the target database and the source API. These are managed via a .env file.

Create a file named .env in the root of the project directory and populate it with the following key-value pairs, using the credentials provided for the assessment:

# PostgreSQL Database Credentials
DB_USER="your_database_user"
DB_PASSWORD="your_database_password"
DB_HOST="your_database_host"
DB_PORT="your_database_port"
DB_NAME="your_database_name"
DB_SCHEMA="your_target_schema"

# API Credentials
API_KEY="your_supabase_api_key"
API_EMAIL="your_api_email"
API_PASSWORD="your_api_password"

4. Database Schema Setup
This project uses Alembic to manage the database schema. To create all necessary tables for both the CSV and API data, run the following command from the project root:

alembic upgrade head

This command will apply all migration scripts in the correct order, creating a complete and correct schema ready for data loading.

5. Running the ETL Pipeline
To execute the entire ETL process for both CSV and API data, simply run the main script from the project root:

python main.py

The script will provide detailed output in the console, indicating the status of each step. A full log file will also be generated in the /logs directory.

Key Design Decisions
This framework was built with several key professional data engineering principles in mind:

Idempotency: The pipeline is designed to be safely re-runnable. The main.py orchestrator calls a truncate_table function before each load. This ensures that each run starts with a clean slate, preventing duplicate data and errors on subsequent executions. This is the standard, reliable pattern for staging data.

Dependency Management: The loading order for both CSV and API tables is explicitly defined. This guarantees that parent tables (e.g., stg_wiserock_user) are always populated before their dependent child tables (e.g., stg_wiserock_note), satisfying all foreign key constraints.

Resilience & Performance:

The ApiExtractor contains robust logic to handle the API's 1000-record pagination limit, ensuring complete data extraction.

The PostgresLoader is designed for stability. It uses a single database connection per table-load to reduce network overhead and contains an automatic retry mechanism to gracefully handle transient network errors (like the SSL error encountered during development).

A targeted, smaller batch size is used for the stg_wiserock__note table to further mitigate network issues with large text fields.

Extensibility: The framework is highly extensible. To add a new data source (e.g., XML files), a developer would simply need to create a new XmlExtractor class and add a corresponding run_xml_pipeline function to main.py, without modifying any of the existing components.