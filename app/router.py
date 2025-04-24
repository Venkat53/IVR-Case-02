from app.nlp import process_user_query, mask_sensitive_data, handle_transfer_conversation

from app.tools import (
    check_balance_tool,
    report_fraud_tool,
    open_account_tool,
    loan_status_tool,
)

class AutoGenRouter:
    def __init__(self):
        self.tool_registry = {
            "balance": check_balance_tool,
            "fraud_report": report_fraud_tool,
            "open_account": open_account_tool,
            "loan_application": loan_status_tool,
        }
        self.confidence_threshold = 0.5

    def route(self, query: str, predicted_intent: str, confidence: float, session_id="user-session"):
        if confidence < self.confidence_threshold:
            return "Low confidence in intent classification. Please rephrase your query."

        # Handle multi-turn transfer flow
        if predicted_intent == "transfer":
            return handle_transfer_conversation(session_id, query)

        # Tool-based one-shot execution
        tool = self.tool_registry.get(predicted_intent)
        if not tool:
            return f"Sorry, I couldn't process the intent '{predicted_intent}' at the moment."

        try:
            result = tool(query)
            return mask_sensitive_data(result)
        except Exception as e:
            return f"Error while handling your request: {str(e)}"
