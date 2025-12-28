import os
import sys
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch from environment
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")

if not DB_CONNECTION_STRING:
    print("Error: DB_CONNECTION_STRING not found in .env file.")
    sys.exit(1)

# Create Engine
try:
    engine = create_engine(DB_CONNECTION_STRING)
    # Quick connection test
    with engine.connect() as connection:
        print("Database Connected Successfully!")
except Exception as e:
    print(f"Database Connection Failed: {e}")
    sys.exit(1)

def get_db_connection():
    """Returns a raw connection object for execution."""
    return engine.connect()