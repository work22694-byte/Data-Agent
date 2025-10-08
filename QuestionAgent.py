import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Load your DB schema into a string
with open("db_schema.txt", "r", encoding="utf-8") as f:
    DB_SCHEMA = f.read()

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Initialize OpenAI LLM
llm = ChatOpenAI(model_name="gpt-4", temperature=0)

# Prompt template: focus on correcting grammar without changing intent
prompt_template = """
You are a question corrector for a database system.

User Question: {user_question}

Database Schema: {db_schema}

Instructions:
- Correct any grammar, spelling, and clarity issues.
- Keep the meaning exactly the same. Do not add or remove intent.
- Make the question ready for understanding by a SQL agent.

Corrected Question:
"""

prompt = PromptTemplate(
    input_variables=["user_question", "db_schema"],
    template=prompt_template
)

agent_chain = LLMChain(llm=llm, prompt=prompt)

def correct_user_question(user_question):
    corrected = agent_chain.run(user_question=user_question, db_schema=DB_SCHEMA)
    return corrected

