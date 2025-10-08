import os
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")

def get_engine():
    """
    Create and return a SQLAlchemy engine for SQL Server using SQL authentication.
    """
    connection_string = (
        f"mssql+pyodbc://{quote_plus(SQL_USERNAME)}:{quote_plus(SQL_PASSWORD)}"
        f"@{SQL_SERVER}/{SQL_DATABASE}?driver={quote_plus(SQL_DRIVER)}"
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
