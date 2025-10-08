import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

# -----------------------------
# Create SQLAlchemy engine (pytds driver)
# -----------------------------
def get_engine():
    """
    Create and return a SQLAlchemy engine for SQL Server using pytds.
    Works without ODBC driver — ideal for Render free tier.
    """
    connection_string = (
        f"mssql+pytds://{SQL_USERNAME}:{SQL_PASSWORD}@{SQL_SERVER}/{SQL_DATABASE}"
    )
    engine = create_engine(connection_string)
    return engine


# -----------------------------
# Execute SQL query
# -----------------------------
def run_query(sql: str) -> pd.DataFrame:
    engine = get_engine()
    try:
        with engine.connect() as conn:
            df = pd.read_sql(sql, conn)
        return df
    except Exception as e:
        print("❌ Error executing query:", e)
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
