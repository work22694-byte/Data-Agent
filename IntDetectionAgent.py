from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import os


class IntentDetectionAgent:
    def __init__(self, llm=None):
        self.llm = llm or ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0
        )

    def detect_intent(self, user_input):
        """
        Returns one of: 'chat', 'query', 'visual', 'query_visual'
        """
        system_prompt = """
        You are an intent detection agent.
        Based on the user's input, determine what the user wants:
        - 'chat' : just general conversation
        - 'query' : they want data from database
        - 'visual' : they want a chart or visualization
        - 'query_visual' : they want data and a chart

        Respond ONLY with one of these keywords.
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]

        response = self.llm(messages).content.strip().lower()

        # Normalize outputs
        if response in ["chat", "query", "visual", "query_visual"]:
            return response
        # fallback
        if "visual" in response and "query" in response:
            return "query_visual"
        elif "visual" in response:
            return "visual"
        elif "query" in response or "data" in response:
            return "query"
        else:
            return "chat"
