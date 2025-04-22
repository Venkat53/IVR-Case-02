from app.nlp import process_user_query, mask_sensitive_data
from app.tools import (
    check_balance_tool,
    transfer_money_tool,
    report_fraud_tool,
    open_account_tool,
    loan_status_tool,
)

class AutoGenRouter:
    def __init__(self):
        # Map available intents to tool functions
        self.tool_registry = {
            "balance": check_balance_tool,
            "transfer": transfer_money_tool,
            "fraud_report": report_fraud_tool,
            "open_account": open_account_tool,
            "loan_application": loan_status_tool,
        }

        self.confidence_threshold = 0.5  # Match with nlp.py

    def route(self, query: str, predicted_intent: str, confidence: float):
        if confidence < self.confidence_threshold:
            return "Low confidence in intent classification. Please rephrase your query."

        # Look up the tool function for the intent
        tool = self.tool_registry.get(predicted_intent)
        if not tool:
            return f"Sorry, I couldn't process the intent '{predicted_intent}' at the moment."

        try:
            # Run the matched tool with the query
            result = tool(query)
            return mask_sensitive_data(result)
        except Exception as e:
            return f"Error while handling your request: {str(e)}"
