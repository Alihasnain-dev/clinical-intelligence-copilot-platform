import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values
from urllib.parse import quote_plus
import pandas as pd
from sqlalchemy import create_engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]
env_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=str(env_path), override=True)
ENV_FALLBACK = dotenv_values(dotenv_path=str(env_path))

# Configuration
POSTGRES_USER = os.getenv("POSTGRES_USER") or ENV_FALLBACK.get("POSTGRES_USER", "psqladmin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD") or ENV_FALLBACK.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST") or ENV_FALLBACK.get("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT") or ENV_FALLBACK.get("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB") or ENV_FALLBACK.get("POSTGRES_DB", "postgres")

# Path to the structured data file
LOCAL_CSV_PATH = "data/1_predictive_data/structured/PatientNoShowKaggleMay2016.csv"
# The name of the table we will create in the database
TABLE_NAME = "appointments"


def require(value: str, name: str) -> str:
    """Ensures required configuration values are available."""
    if not value:
        raise ValueError(f"Environment variable '{name}' is not set.")
    return value


def build_connection_string() -> str:
    """Builds the SQLAlchemy connection string from environment variables."""
    raw_password = require(POSTGRES_PASSWORD, "POSTGRES_PASSWORD")
    host = require(POSTGRES_HOST, "POSTGRES_HOST")
    encoded_password = quote_plus(raw_password)
    return (
        f"postgresql+psycopg2://{POSTGRES_USER}:{encoded_password}"
        f"@{host}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode=require"
    )


def clean_column_names(df):
    """Cleans column names to be SQL-friendly (lowercase, no special chars)."""
    cols = df.columns
    new_cols = []
    for col in cols:
        new_col = col.strip().lower().replace('-', '_')
        new_cols.append(new_col)
    df.columns = new_cols
    return df

def main():
    """
    Main function to read CSV, clean data, and upload to PostgreSQL.
    """
    print("Starting structured data upload to PostgreSQL...")

    if not os.path.exists(LOCAL_CSV_PATH):
        print(f"Error: Data file not found at '{LOCAL_CSV_PATH}'")
        return

    connection_string = build_connection_string()

    # Create a database engine
    try:
        engine = create_engine(connection_string)
        print("Successfully created database engine.")
    except Exception as e:
        print(f"Failed to create database engine: {e}")
        return

    # Read the CSV file into a pandas DataFrame
    print(f"Reading data from '{LOCAL_CSV_PATH}'...")
    df = pd.read_csv(LOCAL_CSV_PATH)
    
    # Clean the column names to be valid in SQL
    df = clean_column_names(df)
    
    # Rename 'no-show' to 'no_show' for consistency
    if 'no_show' in df.columns:
        df.rename(columns={'no_show': 'noshow'}, inplace=True)

    print(f"Uploading {len(df)} rows to the '{TABLE_NAME}' table...")
    
    # Use pandas to_sql to upload the DataFrame to the database.
    # 'if_exists="replace"' will drop the table if it already exists and create a new one.
    # This is useful for re-running the script during development.
    try:
        df.to_sql(TABLE_NAME, engine, if_exists='replace', index=False)
        print("Data upload completed successfully.")
    except Exception as e:
        print(f"An error occurred during data upload: {e}")
    
    print("\n-------------------------------------")
    print("Structured data processing finished.")
    print("-------------------------------------")

if __name__ == "__main__":
    main()
