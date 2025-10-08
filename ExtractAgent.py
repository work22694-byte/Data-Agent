import os
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

DB_CONNECTION = os.getenv("DB_CONNECTION", "mssql+pyodbc")
DB_HOST = os.getenv("DB_HOST", "localhost\\SQLEXPRESS")
DB_PORT = os.getenv("DB_PORT", "1433")
DB_DATABASE = os.getenv("DB_DATABASE", "master")
DB_USERNAME = os.getenv("DB_USERNAME", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# -----------------------------
# Create SQLAlchemy engine
# -----------------------------
def get_engine():
    """
    Returns a SQLAlchemy engine using either Windows Auth or SQL Auth.
    """
    if DB_USERNAME and DB_PASSWORD:
        # SQL Server Authentication
        connection_string = (
            f"mssql+pyodbc://{quote_plus(DB_USERNAME)}:{quote_plus(DB_PASSWORD)}"
            f"@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?driver={quote_plus(DB_DRIVER)}"
        )
    else:
        # Windows Authentication
        connection_string = (
            f"mssql+pyodbc://@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
            f"?driver={quote_plus(DB_DRIVER)}&trusted_connection=yes"
        )

    engine = create_engine(connection_string, fast_executemany=True)
    return engine

# -----------------------------
# Execute SQL query
# -----------------------------
def run_query(sql: str) -> pd.DataFrame:
    """
    Execute a SQL query and return results as a pandas DataFrame.
    """
    engine = get_engine()
    try:
        with engine.connect() as conn:
            df = pd.read_sql(sql, conn)
        return df
    except Exception as e:
        print("Error executing query:", e)
        return pd.DataFrame()

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    sql_query = input("Enter your SQL query: ")
    df = run_query(sql_query)
    if not df.empty:
        print("\nQuery Results:")
        print(df)
    else:
        print("No results or query failed.")
