import os
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# --- Memory store for learning ---
query_history = []

def remember_query(user_question, sql_query):
    query_history.append({"question": user_question, "sql": sql_query})


# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# -----------------------------
# Load schema automatically
# -----------------------------
def load_schema(file_path: str) -> str:
    """
    Load CSV schema and format for LLM.
    Automatically detects Table, Column, and DataType columns.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Schema file not found: {file_path}")

    df = pd.read_csv(file_path)
    df.columns = [c.strip() for c in df.columns]

    table_col = next((c for c in df.columns if "table" in c.lower()), None)
    column_col = next((c for c in df.columns if "column" in c.lower()), None)
    dtype_col = next((c for c in df.columns if "type" in c.lower()), None)

    if not table_col or not column_col or not dtype_col:
        raise KeyError(f"Could not detect Table/Column/Datatype columns. Found columns: {df.columns}")

    schema_str = ""
    for table in df[table_col].unique():
        subset = df[df[table_col] == table]
        schema_str += f"\n\nTable: {table}\nColumns:\n"
        for _, row in subset.iterrows():
            schema_str += f"  - {row[column_col]} ({row[dtype_col]})\n"
    return schema_str.strip()

DB_SCHEMA = load_schema("schema.csv")  # <-- put your CSV in same folder

# -----------------------------
# Initialize LLM
# -----------------------------
llm_query_builder = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)

# -----------------------------
# Helper: clean markdown backticks from LLM output
# -----------------------------
def clean_sql(sql: str) -> str:
    sql = sql.strip()
    if sql.startswith("```sql"):
        sql = sql[6:]
    if sql.startswith("```"):
        sql = sql[3:]
    if sql.endswith("```"):
        sql = sql[:-3]
    return sql.strip()

def wants_visualization(question: str) -> bool:
    """
    Detect if user wants to visualize data.
    """
    keywords = ["chart", "plot", "graph", "visual", "visualize", "bar", "pie", "line"]
    return any(k in question.lower() for k in keywords)


# -----------------------------
# Generate SQL Server query
# -----------------------------
def generate_sql_query(user_question: str) -> str:
    """
    Convert natural language question into executable SQL Server query.
    - Ignores any LIMIT (MySQL/PostgreSQL).
    - Only uses TOP N if explicitly requested in SQL Server style.
    - Returns clean SQL string ready for SSMS.
    """
    prompt = f"""
You are an expert SQL Server query generator.
Database schema:
{DB_SCHEMA}

Instructions:
1. Generate correct SQL Server query based on the user's question.
2. Use only existing tables and columns.
3. NEVER use destructive commands (DELETE, DROP, ALTER, TRUNCATE).
4. Do NOT include LIMIT or any MySQL/PostgreSQL syntax.
5. Only include TOP N if the user explicitly requests SQL Server style (e.g., 'TOP 5').
6. Return ONLY the SQL query, fully executable in SSMS.
7. Do NOT include any markdown formatting like ```sql or ```.
8. If user says "last year" or "in the past 12 months", treat them as the same time range:
PROCESSINGDATE >= DATEADD(YEAR, -1, GETDATE())

Example 1:
User Question: How many meters processed for Asda last year?
SQL: SELECT SUM(METER) AS TotalMetersProcessed
     FROM PROCESSING
     WHERE UPPER(CUSTOMER) LIKE UPPER('%ASDA%')
     AND PROCESSINGDATE >= DATEADD(YEAR, -1, GETDATE());


User Question: {user_question}
SQL Query:
"""
    response = llm_query_builder.invoke(prompt)
    sql = response.content.strip()
    sql = clean_sql(sql)
    return sql

# -----------------------------
# Interactive usage
# -----------------------------
if __name__ == "__main__":
    print("Welcome! Ask questions about your database (type 'exit' to quit):\n")
    while True:
        q = input("Your question: ")
        if q.lower() in ["exit", "quit"]:
            break
        try:
            if wants_visualization(q):
                print("\nIt looks like you want a visualization.")
                chart_type = input("Which type of chart? (bar, line, pie): ").strip().lower()
                column_name = input("Enter the column for X-axis: ").strip()
                value_column = input("Enter the column for Y-axis: ").strip()
                print(f"✅ Got it: {chart_type} of {value_column} by {column_name}")

            sql_query = generate_sql_query(q)
            print("\nGenerated SQL Query (SSMS-ready):\n", sql_query, "\n")

            # Remember it (so the agent 'learns')
            remember_query(q, sql_query)

        except Exception as e:
            print("Error:", e)
