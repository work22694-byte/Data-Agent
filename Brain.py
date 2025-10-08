from IntDetectionAgent import IntentDetectionAgent
from QueryAgent import generate_sql_query
from ExtractAgent import run_query
from ChatAgent import process_chat
from QuestionAgent import correct_user_question
from parser import DataFormatterAgent   # <-- use the new class


class BrainAgent:
    def __init__(self):
        # Initialize agents
        self.intent_agent = IntentDetectionAgent()
        self.data_formatter = DataFormatterAgent()   # ✅ new
        self.context_history = []  # optional memory

    def handle_input(self, user_input: str):
        """
        Main orchestrator:
        1. Detect intent
        2. Route accordingly (query / visual / both / chat)
        3. Return response or visualization
        """
        # Step 1: Detect intent
        intent = self.intent_agent.detect_intent(user_input)

        # -------------------------------
        # QUERY: Data question only
        # -------------------------------
        if intent == "query":
            corrected_question = correct_user_question(user_input)
            query = generate_sql_query(corrected_question)
            results_df = run_query(query)

            # ✅ Clean and format the DataFrame before sending to chat
            csv_path, cleaned_df = self.data_formatter.process_data(results_df)

            chat_input = (
                f"User asked: {user_input}\n"
                f"Corrected question: {corrected_question}\n"
                f"Here is the formatted query result:\n{cleaned_df.to_string(index=False)}\n"
                "Summarize and explain the results clearly."
                "Assume you already know the data. Do not say things like 'based on the data provided."
                "' Speak as if you are fully aware of the data and explain it directly to the user."
            )
            response = process_chat(chat_input)



        # -------------------------------
        # CHAT: General conversation
        # -------------------------------
        else:
            response = process_chat(user_input)

        # -------------------------------
        # Update context
        # -------------------------------
        self.context_history.append({
            "user_input": user_input,
            "intent": intent,
            "response": response
        })

        return response
