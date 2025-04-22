import os
import pandas as pd
import random
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("D:/IVR Case-02/sample_generation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define output path
output_path = "D:/IVR Case-02/app/data/banking_intents.csv"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Define intents and query templates (~50 intents)
intents_templates = {
    "balance": [
        "What is my {account_type} balance?",
        "Check my {account_type} funds",
        "How much money is in my {account_type}?",
        "Show my {account_type} total",
        "Tell me my {account_type} amount",
        "Verify my {account_type} balance",
        "What’s the balance for my {account_type}?",
        "Give me my {account_type} status"
    ],
    "transfer": [
        "Transfer {amount} to my {account_type}",
        "Send {amount} to {recipient}",
        "Move {amount} to my {account_type} account",
        "Wire {amount} to {recipient}",
        "Shift {amount} to another {account_type}",
        "Deposit {amount} to {recipient}’s account",
        "Send {amount} {currency} overseas",
        "Transfer funds to my {account_type}"
    ],
    "block_card": [
        "Block my {card_type} card",
        "Freeze my {card_type} now",
        "Disable my stolen {card_type}",
        "Lock my {card_type} immediately",
        "Restrict my {card_type} card",
        "Secure my {card_type} due to theft",
        "Stop my {card_type} from being used",
        "Cancel my lost {card_type}"
    ],
    "payment": [
        "Pay my {card_type} bill",
        "Settle my {card_type} payment",
        "Make a {card_type} payment",
        "Clear my {card_type} balance",
        "Send payment for my {card_type}",
        "Process my {card_type} monthly payment",
        "Pay off my {card_type} dues",
        "Cover my {card_type} charges"
    ],
    "open_account": [
        "Open a new {account_type} account",
        "Start a {account_type} account",
        "Create a {account_type} profile",
        "Initiate a new {account_type} account",
        "Establish a {account_type} account",
        "Set up a {account_type} account",
        "Begin a {account_type} banking account",
        "Open an account for {account_type}"
    ],
    "close_account": [
        "Close my {account_type} account",
        "Terminate my {account_type} profile",
        "End my {account_type} account",
        "Cancel my {account_type} account",
        "Shut down my {account_type}",
        "Deactivate my {account_type} account",
        "Close out my {account_type} banking",
        "Stop my {account_type} account"
    ],
    "replace_card": [
        "Get a new {card_type} card",
        "Order a replacement {card_type}",
        "I need a new {card_type} card",
        "Send me a new {card_type}",
        "Replace my lost {card_type}",
        "Provide a new {card_type}",
        "Issue a replacement {card_type}",
        "Renew my {card_type} card"
    ],
    "transaction_history": [
        "Check my recent {account_type} transactions",
        "Show my last {account_type} payments",
        "What are my recent {account_type} charges?",
        "List my {account_type} account activity",
        "Review my {account_type} transaction log",
        "See my {account_type} purchase history",
        "Display my recent {account_type} transfers",
        "View my {account_type} transaction details"
    ],
    "loan_application": [
        "Apply for a {loan_type} loan",
        "Get a {loan_type} loan",
        "I want to borrow for a {loan_type}",
        "Submit a {loan_type} loan request",
        "Start a {loan_type} loan application",
        "Apply for {loan_type} financing",
        "Request a {loan_type} loan",
        "Begin a {loan_type} loan process"
    ],
    "update_info": [
        "Update my {info_type} details",
        "Change my {info_type}",
        "Modify my {info_type} information",
        "Edit my {info_type} on file",
        "Revise my {info_type} details",
        "Update my {info_type} for the account",
        "Change my {info_type} contact info",
        "Adjust my {info_type} records"
    ],
    "customer_support": [
        "Help me with my {issue_type}",
        "I need assistance with my {issue_type}",
        "Support for my {issue_type} issue",
        "Guide me with my {issue_type} problem",
        "Aid with my {issue_type} error",
        "Assist with my {issue_type} concern",
        "Help with my {issue_type} query",
        "Resolve my {issue_type} issue"
    ],
    "credit_limit_increase": [
        "Raise my {card_type} credit limit",
        "Increase my {card_type} limit",
        "Extend my {card_type} credit allowance",
        "Boost my {card_type} spending limit",
        "Up my {card_type} credit ceiling",
        "Request a higher {card_type} limit",
        "Elevate my {card_type} card limit",
        "Expand my {card_type} credit"
    ],
    "dispute_charge": [
        "Dispute a {account_type} transaction",
        "Contest a {account_type} charge",
        "Challenge a {account_type} payment",
        "Report an incorrect {account_type} charge",
        "Dispute a {account_type} fee",
        "Question a {account_type} transaction",
        "Flag a {account_type} charge error",
        "Appeal a {account_type} billing issue"
    ],
    "pin_reset": [
        "Reset my {card_type} PIN",
        "Change my {card_type} PIN",
        "Update my {card_type} PIN code",
        "Set a new {card_type} PIN",
        "Renew my {card_type} PIN",
        "Modify my {card_type} PIN number",
        "Create a new {card_type} PIN",
        "Reset PIN for my {card_type}"
    ],
    "letter_status": [
        "Check my letter status",
        "What’s the status of my letter?",
        "Track my letter delivery",
        "Verify my letter processing",
        "Update on my letter request",
        "Check if my letter was sent",
        "See my letter status details",
        "Confirm my letter’s progress"
    ],
    "fraud_report": [
        "Report a fraudulent {account_type} charge",
        "Flag a {account_type} scam transaction",
        "Report fraud on my {account_type}",
        "Notify about a {account_type} fraud",
        "Alert for {account_type} suspicious activity",
        "Report a {account_type} unauthorized charge",
        "Flag fraudulent {account_type} activity",
        "Raise a {account_type} fraud concern"
    ],
    "account_statement": [
        "Send my {account_type} statement",
        "Get my {account_type} monthly statement",
        "Provide my {account_type} account statement",
        "Email my {account_type} statement",
        "Share my {account_type} transaction statement",
        "Download my {account_type} statement",
        "View my {account_type} statement",
        "Request a {account_type} statement"
    ],
    "card_activation": [
        "Activate my new {card_type}",
        "Enable my {card_type} card",
        "Start using my {card_type}",
        "Turn on my {card_type} card",
        "Activate my {card_type} for use",
        "Set up my new {card_type}",
        "Initialize my {card_type} card",
        "Make my {card_type} active"
    ],
    "interest_rates": [
        "What are the {account_type} interest rates?",
        "Tell me about {account_type} interest",
        "Check {account_type} interest rates",
        "Provide {account_type} rate details",
        "What’s the interest for {account_type}?",
        "Share {account_type} interest info",
        "Explain {account_type} rates",
        "Give me {account_type} interest details"
    ],
    "fee_inquiry": [
        "What are the {account_type} fees?",
        "Check {account_type} account fees",
        "Tell me about {account_type} charges",
        "List the {account_type} fees",
        "Explain {account_type} fee structure",
        "Provide {account_type} fee details",
        "What fees apply to {account_type}?",
        "Share {account_type} fee information"
    ],
    "branch_locator": [
        "Find a {bank} branch near me",
        "Locate a {bank} branch",
        "Where is the nearest {bank} branch?",
        "Show me {bank} branch locations",
        "Tell me about {bank} branch addresses",
        "Find {bank} branches in my area",
        "List {bank} branch details",
        "Give me {bank} branch information"
    ],
    "foreign_exchange": [
        "Check {currency} exchange rates",
        "What’s the {currency} conversion rate?",
        "Provide {currency} forex rates",
        "Tell me about {currency} exchange",
        "Convert {currency} to dollars",
        "Show {currency} exchange details",
        "What are {currency} rates today?",
        "Give me {currency} forex info"
    ],
    "bill_payment": [
        "Pay my {bill_type} bill",
        "Settle my {bill_type} payment",
        "Process a {bill_type} bill payment",
        "Clear my {bill_type} dues",
        "Send payment for {bill_type}",
        "Cover my {bill_type} charges",
        "Make a {bill_type} payment",
        "Pay off my {bill_type}"
    ],
    "account_verification": [
        "Verify my {account_type} account",
        "Confirm my {account_type} details",
        "Check my {account_type} status",
        "Validate my {account_type} profile",
        "Ensure my {account_type} is active",
        "Authenticate my {account_type}",
        "Verify {account_type} account info",
        "Confirm my {account_type} setup"
    ],
    "overdraft_protection": [
        "Enable overdraft for my {account_type}",
        "Set up {account_type} overdraft protection",
        "Activate overdraft on {account_type}",
        "Turn on {account_type} overdraft",
        "Add overdraft to my {account_type}",
        "Enable {account_type} overdraft feature",
        "Set overdraft for {account_type}",
        "Protect my {account_type} with overdraft"
    ],
    "mobile_banking": [
        "Set up {account_type} mobile banking",
        "Access my {account_type} via app",
        "Enable {account_type} online banking",
        "Register for {account_type} mobile app",
        "Activate {account_type} mobile access",
        "Set up {account_type} app banking",
        "Use my {account_type} on mobile",
        "Enable {account_type} mobile services"
    ],
    "account_freeze": [
        "Freeze my {account_type} account",
        "Suspend my {account_type} account",
        "Put a hold on my {account_type}",
        "Lock my {account_type} temporarily",
        "Restrict my {account_type} account",
        "Pause my {account_type} activity",
        "Secure my {account_type} with a freeze",
        "Stop transactions on my {account_type}"
    ],
    "direct_deposit": [
        "Set up direct deposit for {account_type}",
        "Enable direct deposit to my {account_type}",
        "Add direct deposit for {account_type}",
        "Configure {account_type} for direct deposit",
        "Start direct deposit to {account_type}",
        "Set my {account_type} for direct deposit",
        "Activate direct deposit on {account_type}",
        "Link {account_type} to direct deposit"
    ],
    "stop_payment": [
        "Stop a payment on my {account_type}",
        "Cancel a {account_type} transaction",
        "Halt a payment from my {account_type}",
        "Block a {account_type} payment",
        "Stop a check on my {account_type}",
        "Prevent a {account_type} payment",
        "Cancel a pending {account_type} payment",
        "Stop payment for {account_type} transaction"
    ],
    "credit_score_check": [
        "Check my credit score",
        "What is my credit score?",
        "Provide my credit score details",
        "Tell me my current credit score",
        "Show my credit score report",
        "Verify my credit score",
        "Get my credit score information",
        "Review my credit score status"
    ],
    "mortgage_inquiry": [
        "Inquire about a {loan_type} mortgage",
        "Tell me about {loan_type} mortgage options",
        "What are {loan_type} mortgage rates?",
        "Provide {loan_type} mortgage details",
        "Explain {loan_type} mortgage terms",
        "Get info on {loan_type} mortgage",
        "Check {loan_type} mortgage availability",
        "Share {loan_type} mortgage information"
    ],
    "investment_options": [
        "What are my {account_type} investment options?",
        "Tell me about {account_type} investments",
        "Provide {account_type} investment details",
        "Show {account_type} investment plans",
        "Explain {account_type} investment opportunities",
        "Check {account_type} investment choices",
        "List {account_type} investment products",
        "Share {account_type} investment info"
    ],
    "savings_goal": [
        "Set a savings goal for my {account_type}",
        "Create a {account_type} savings plan",
        "Start a savings goal on {account_type}",
        "Establish a {account_type} savings target",
        "Add a savings goal to my {account_type}",
        "Plan a savings goal for {account_type}",
        "Set up {account_type} savings objective",
        "Define a {account_type} savings goal"
    ],
    "card_rewards": [
        "Check my {card_type} rewards",
        "What are my {card_type} reward points?",
        "Show my {card_type} rewards balance",
        "Tell me about {card_type} rewards",
        "Provide {card_type} rewards details",
        "Verify my {card_type} rewards status",
        "List my {card_type} rewards earnings",
        "Get my {card_type} rewards information"
    ],
    "account_transfer_limits": [
        "What are {account_type} transfer limits?",
        "Check {account_type} transfer restrictions",
        "Tell me about {account_type} transfer caps",
        "Provide {account_type} transfer limit details",
        "Explain {account_type} transfer rules",
        "Show {account_type} transfer boundaries",
        "List {account_type} transfer constraints",
        "Share {account_type} transfer limit info"
    ],
    "check_order": [
        "Order checks for my {account_type}",
        "Get new checks for {account_type}",
        "Request checks for my {account_type}",
        "Provide checks for {account_type}",
        "Send me {account_type} checks",
        "Order new {account_type} checkbook",
        "Issue checks for {account_type}",
        "Get a checkbook for {account_type}"
    ],
    "atm_withdrawal": [
        "Withdraw {amount} from ATM for {account_type}",
        "Get {amount} from ATM using {account_type}",
        "Take out {amount} at ATM from {account_type}",
        "ATM withdrawal of {amount} from {account_type}",
        "Pull {amount} from {account_type} at ATM",
        "Extract {amount} via ATM for {account_type}",
        "Get cash of {amount} from {account_type} ATM",
        "Withdraw {amount} at ATM for {account_type}"
    ],
    "travel_notification": [
        "Set a travel notification for my {card_type}",
        "Notify travel plans for {card_type}",
        "Add a travel alert for my {card_type}",
        "Inform about travel for {card_type}",
        "Set {card_type} travel notice",
        "Update {card_type} with travel plans",
        "Register travel for my {card_type}",
        "Alert bank about {card_type} travel"
    ],
    "wire_transfer": [
        "Initiate a wire transfer from {account_type}",
        "Send a wire transfer to {recipient}",
        "Process a {account_type} wire transfer",
        "Wire {amount} from {account_type}",
        "Transfer {amount} via wire to {recipient}",
        "Set up a wire from {account_type}",
        "Send wire transfer from {account_type}",
        "Execute a {account_type} wire transfer"
    ],
    "account_balance_alert": [
        "Set a balance alert for {account_type}",
        "Notify me about {account_type} balance",
        "Add a {account_type} balance alert",
        "Alert me when {account_type} balance changes",
        "Create a {account_type} balance notification",
        "Set up {account_type} balance monitoring",
        "Enable {account_type} balance alerts",
        "Track {account_type} balance with alerts"
    ],
    "card_expiration": [
        "Check my {card_type} expiration date",
        "What’s the expiry of my {card_type}?",
        "Verify {card_type} expiration details",
        "Tell me when my {card_type} expires",
        "Show {card_type} expiry information",
        "Get {card_type} expiration status",
        "Provide {card_type} expiry date",
        "Confirm my {card_type} expiration"
    ],
    "business_account_inquiry": [
        "Inquire about my {account_type} business account",
        "Check details of {account_type} business account",
        "Tell me about my {account_type} business profile",
        "Provide {account_type} business account info",
        "What’s the status of my {account_type} business?",
        "Show {account_type} business account details",
        "Explain {account_type} business account features",
        "Get info on {account_type} business account"
    ],
    "tax_document_request": [
        "Request tax documents for {account_type}",
        "Send my {account_type} tax forms",
        "Provide {account_type} tax statements",
        "Get tax documents for my {account_type}",
        "Share {account_type} tax paperwork",
        "Email {account_type} tax records",
        "Download {account_type} tax documents",
        "Issue {account_type} tax forms"
    ],
    "account_nickname": [
        "Set a nickname for my {account_type}",
        "Change {account_type} account nickname",
        "Add a nickname to my {account_type}",
        "Update {account_type} with a nickname",
        "Assign a nickname to {account_type}",
        "Modify {account_type} account name",
        "Give my {account_type} a nickname",
        "Set {account_type} nickname"
    ],
    "recurring_payment": [
        "Set up a recurring payment for {bill_type}",
        "Enable recurring {bill_type} payments",
        "Add a {bill_type} recurring payment",
        "Schedule recurring {bill_type} payments",
        "Create a {bill_type} recurring payment",
        "Set {bill_type} payment to recur",
        "Activate recurring {bill_type} payment",
        "Establish {bill_type} recurring payment"
    ],
    "joint_account": [
        "Add a joint owner to my {account_type}",
        "Set up a joint {account_type} account",
        "Include a co-owner for {account_type}",
        "Create a joint {account_type} profile",
        "Link a joint owner to {account_type}",
        "Establish a joint {account_type}",
        "Add someone to my {account_type} account",
        "Set {account_type} as joint account"
    ],
    "card_block_notification": [
        "Notify me if my {card_type} is blocked",
        "Alert me about {card_type} block status",
        "Set a {card_type} block notification",
        "Inform me when {card_type} is restricted",
        "Enable {card_type} block alerts",
        "Track {card_type} block status",
        "Send {card_type} block notifications",
        "Monitor {card_type} for block alerts"
    ]
}

# Define variations for placeholders
variations = {
    "account_type": ["checking", "savings", "business", "personal", "joint"],
    "card_type": ["credit", "debit", "visa", "mastercard"],
    "amount": ["$50", "$100", "$200", "fifty dollars", "one hundred dollars"],
    "recipient": ["friend", "family", "contact", "sister", "brother"],
    "currency": ["USD", "EUR", "GBP", "JPY"],
    "loan_type": ["personal", "car", "home", "business"],
    "info_type": ["phone number", "email", "address", "contact", "mailing address"],
    "issue_type": ["account", "card", "transaction", "login", "billing"],
    "bank": ["bank", "local bank", "branch", "ATM"],
    "bill_type": ["utility", "phone", "internet", "electricity"]
}

# Generate samples
def generate_samples(intent, templates, num_samples=40):
    samples = []
    for _ in range(num_samples):
        template = random.choice(templates)
        query = template
        for placeholder, options in variations.items():
            if f"{{{placeholder}}}" in query:
                query = query.replace(f"{{{placeholder}}}", random.choice(options))
        samples.append({"query": query, "intent": intent})
    return samples

# Generate dataset
data = []
for intent, templates in intents_templates.items():
    logger.info(f"Generating samples for intent: {intent}")
    samples = generate_samples(intent, templates, num_samples=40)
    data.extend(samples)

# Shuffle and create DataFrame
random.shuffle(data)
df = pd.DataFrame(data)

# Save to CSV
try:
    logger.info(f"Saving {len(df)} samples to {output_path}")
    df.to_csv(output_path, index=False)
    logger.info(f"Successfully saved to {output_path}")
    logger.info(f"Intents: {sorted(df['intent'].unique())}")
    logger.info(f"Sample count per intent:\n{df['intent'].value_counts().to_dict()}")
except Exception as e:
    logger.error(f"Error saving CSV: {str(e)}")
    raise

# Verify file
if os.path.exists(output_path):
    logger.info(f"File verified at {output_path}")
    logger.info(f"Total samples: {len(df)}")
else:
    logger.error(f"File not found at {output_path}")
    raise FileNotFoundError(f"CSV not created at {output_path}")