import requests
from langchain.tools import tool

API_BASE_URL = "http://localhost:5001"  # <-- Replace with your actual API base URL

@tool
def check_balance_tool(query: str) -> str:
    """
    Check the current account balance of the user.
    """
    try:
        response = requests.post(f"{API_BASE_URL}/balance", json={"query": query})
        response.raise_for_status()
        data = response.json()
        return data.get("message", "Balance info not available.")
    except Exception as e:
        return "Unable to fetch account balance right now."

@tool
def transfer_money_tool(query: str) -> str:
    """
    Initiate a money transfer to another account.
    """
    try:
        response = requests.post(f"{API_BASE_URL}/transfer", json={"query": query})
        response.raise_for_status()
        data = response.json()
        return data.get("message", "Transfer info not available.")
    except Exception as e:
        return "Unable to initiate money transfer at the moment."

@tool
def report_fraud_tool(query: str) -> str:
    """
    Report a fraudulent or suspicious transaction.
    """
    try:
        response = requests.post(f"{API_BASE_URL}/report-fraud", json={"query": query})
        response.raise_for_status()
        data = response.json()
        return data.get("message", "Fraud report not processed.")
    except Exception as e:
        return "Unable to report fraud right now."

@tool
def open_account_tool(query: str) -> str:
    """
    Send a link to open a new bank account.
    """
    try:
        response = requests.post(f"{API_BASE_URL}/open-account", json={"query": query})
        response.raise_for_status()
        data = response.json()
        return data.get("message", "Account opening link not sent.")
    except Exception as e:
        return "Unable to send account opening link."

@tool
def loan_status_tool(query: str) -> str:
    """
    Retrieve the status of a loan application.
    """
    try:
        response = requests.post(f"{API_BASE_URL}/loan-status", json={"query": query})
        response.raise_for_status()
        data = response.json()
        return data.get("message", "Loan status not available.")
    except Exception as e:
        return "Unable to retrieve loan status right now."
