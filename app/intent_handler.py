def handle_intent(intent):
    responses = {
        "balance": "Your current balance is $1,200.",
        "transfer": "Please specify the amount and recipient.",
        "transaction_history": "Fetching your last 5 transactions.",
        "lost_card": "We have blocked your card. A new card will be sent to your address.",
        "block_card": "Card has been blocked successfully.",
        "reset_pin": "To reset your PIN, we'll send an OTP to your registered number.",
        "faq": "Visit our FAQ page at bank.com/faq",
        "greeting": "Hi there! How can I assist you today?",
        "complaint": "We are sorry to hear that. Please describe your issue.",
        "loan_inquiry": "Are you looking for personal or home loans?",
        "credit_card": "Would you like to apply for a new credit card or manage an existing one?",
        "debit_card": "You can manage your debit card from the cards section in the app.",
        "investment": "We offer mutual funds and fixed deposits. Would you like help with these?",
        "account_opening": "You can open a new account digitally via our app.",
        "support": "Our support team is available 24/7.",
        "exit": "Thank you for contacting us. Goodbye!",
        "fallback": "I'm sorry, I didn't understand that. Can you please rephrase?"
    }
    return responses.get(intent, "I'm sorry, I didn't understand that. Can you please rephrase?")