from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool

# Import the settings object from our config module.
# This is how we access the DATABASE_URL we defined earlier.
from src.config import settings

def get_engine() -> Engine:
    """
    Creates and returns a SQLAlchemy database engine.

    The engine is the starting point for any SQLAlchemy application.
    It's the central source of connections to a particular database,
    providing both a factory and a pool of connections.

    Returns:
        Engine: A SQLAlchemy Engine instance connected to the database
                specified in the settings.
    """
    try:
        # Create the engine using the DATABASE_URL from our settings.
        # The `echo=False` argument means SQLAlchemy will not log every
        # single SQL statement it executes, keeping our logs clean.
        # For debugging, you could set this to True.
        engine = create_engine(settings.DATABASE_URL, poolclass=NullPool, connect_args={"sslmode": "require"}, echo=False)
        
        # Test the connection to fail fast if credentials are wrong
        with engine.connect() as connection:
            print("Database connection successful.")
        
        return engine
    except Exception as e:
        print(f"Error creating database engine: {e}")
        # Re-raise the exception to stop the application if the DB is unavailable.
        raise

# Create a single, reusable engine instance that the rest of
# our application can import and use.
engine = get_engine()

