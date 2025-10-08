import os
import pandas as pd
from io import StringIO
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class DataFormatterAgent:
    def __init__(self, model_name="gpt-4o-mini", temperature=0):
        """Initialize formatter with optional LLM (for messy text parsing)."""
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=OPENAI_API_KEY
        )

    def process_data(self, data, output_path="formatted_output.csv"):
        """
        Process data from raw text or DataFrame.
        Returns cleaned DataFrame and saves as CSV.
        """
        if isinstance(data, pd.DataFrame):
            df = data.copy()

            # Normalize column names
            df.columns = [col.strip().replace(" ", "_").upper() for col in df.columns]

            # Detect numeric-like columns and clean only those
            for col in df.columns:
                if df[col].dtype == object:
                    # Check if most values are numeric-looking
                    numeric_like = df[col].astype(str).str.replace(r"[^\d.]", "", regex=True)
                    valid_numeric_ratio = (
                        numeric_like.str.match(r"^\d+(\.\d+)?$").sum() / len(df[col])
                    )

                    # Clean only if it's mostly numeric
                    if valid_numeric_ratio > 0.6:
                        df[col] = (
                            df[col]
                            .astype(str)
                            .str.replace(r"[^\d.]", "", regex=True)
                            .replace("", pd.NA)
                        )
                        df[col] = pd.to_numeric(df[col], errors="coerce")

            # Drop completely empty rows
            df.dropna(how="all", inplace=True)

            df.to_csv(output_path, index=False)
            return output_path, df

        elif isinstance(data, str):
            system_prompt = """
            You are a data parser. Convert raw text about items and quantities 
            into clean 2-column CSV format with headers:
            ITEMNAME, TotalQuantity
            Keep item names as text exactly; parse only numeric values as quantities.
            Do NOT include markdown or explanations — output only CSV.
            """

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=data)
            ]

            response = self.llm.invoke(messages)
            csv_text = response.content.strip()
            df = pd.read_csv(StringIO(csv_text))
            df.to_csv(output_path, index=False)
            print(f"✅ Raw text parsed and saved to: {output_path}")
            return output_path, df

        else:
            raise TypeError(
                f"Unsupported input type: {type(data)}. Expected str or pandas.DataFrame."
            )


    # optional alias
    def process_and_save(self, data, output_path="formatted_output.csv"):
        """Alias for process_data for backward compatibility"""
        return self.process_data(data, output_path)
