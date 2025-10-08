import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.vectorstores import Chroma

# --- Load environment ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Globals ---
chat_vectorstore = None
llm = None

# --- Initialize memory + LLM ---
def init_chat_agent():
    global llm, chat_vectorstore

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    chat_vectorstore = Chroma(
        collection_name="chat_memory",
        embedding_function=embeddings,
        persist_directory="chroma_store_chat"
    )
    llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=0.7  # more natural responses
    )

init_chat_agent()

# --- Main Chat Processing ---
def process_chat(user_input: str):
    global llm, chat_vectorstore

    if user_input.lower() in ["reset", "clear memory"]:
        reset_chat_memory()
        return "✅ Chat memory cleared."

    # Retrieve relevant past messages
    retriever = chat_vectorstore.as_retriever(search_kwargs={"k": 5})
    docs = retriever.get_relevant_documents(user_input)
    long_term_context = "\n---\n".join([d.page_content for d in docs])

    prompt = f"""
You are a friendly assistant with memory.

Memory context:
{long_term_context}

User said: {user_input}
Respond naturally and conversationally.
"""
    # Get AI response
    response = llm.predict(prompt)

    # Save both user input and AI response to memory
    chat_vectorstore.add_texts([user_input, response])
    chat_vectorstore.persist()

    return response

# --- Reset Memory ---
def reset_chat_memory():
    global chat_vectorstore
    try:
        if hasattr(chat_vectorstore, "delete_collection"):
            chat_vectorstore.delete_collection()
    except Exception as e:
        print("Error resetting memory:", e)

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    chat_vectorstore = Chroma(
        collection_name="chat_memory",
        embedding_function=embeddings,
        persist_directory="chroma_store_chat"
    )
    print("🧠 Chat memory reset.")

# --- CLI test ---
if __name__ == "__main__":
    print("🤖 Chat Agent Ready. Type 'reset' to clear memory, 'exit' to quit.")
    while True:
        q = input("You: ")
        if q.lower() in ["exit", "quit"]:
            break
        print("AI:", process_chat(q))




