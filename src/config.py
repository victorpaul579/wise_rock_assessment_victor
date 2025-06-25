import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Build the path to the .env file from the current file's location
# This makes the path robust, regardless of where the script is run from.
# Path(__file__) is the path to this config.py file.
# .parent is the 'src' directory.
# .parent again is the project root directory.
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    """
    A class to hold all application settings, loaded from environment variables.
    This provides a single, organized source of truth for configuration.
    """
    # Database Settings
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD_RAW: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432)) # Default to 5432 if not set
    DB_NAME: str = os.getenv("DB_NAME")
    DB_SCHEMA: str = os.getenv("DB_SCHEMA", "public") # Default to public if not set

    # URL-encode the password to handle special characters like '@'
    # This is a critical step for robust connection strings.
    DB_PASSWORD_ENCODED: str = quote_plus(DB_PASSWORD_RAW)

    # Database URL for SQLAlchemy
    # The f-string constructs the full connection URL from the individual components,
    # now using the safely encoded password.
    DATABASE_URL: str = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Project Directories
    # This robustly defines the root directory of the project.
    ROOT_DIR = Path(__file__).parent.parent
    DATA_DIR = ROOT_DIR / "data"


    # API config
    API_KEY: str = os.getenv("API_KEY")
    API_EMAIL: str = os.getenv("API_EMAIL")
    API_PASSWORD: str = os.getenv("API_PASSWORD")

    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    USE_PARALLEL = os.getenv("USE_PARALLEL", "false").lower() == "true"


    def __init__(self):
        # A simple validation to ensure critical database settings are present.
        # This will cause the application to fail fast if the .env file is missing
        # or misconfigured, which is good practice.
        if not all([self.DB_USER, self.DB_PASSWORD_RAW, self.DB_HOST, self.DB_NAME]):
            raise ValueError("One or more critical database environment variables are missing.")

# Create a single instance of the Settings class.
# Other modules in our application will import this `settings` object
# to access any configuration value they need.
settings = Settings()
