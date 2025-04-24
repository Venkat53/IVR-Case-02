import json
import logging
import re
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from app.tools import transfer_money_tool

# Set up logging
logging.basicConfig(level=logging.INFO, filename='intent_classifier.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize ChromaDB
persist_directory = "./chromadb_store"
embedding_function = DefaultEmbeddingFunction()
chroma_client = chromadb.Client(chromadb.config.Settings(persist_directory=persist_directory))
collection = chroma_client.get_or_create_collection(name="session_context", embedding_function=embedding_function)

# Load model
model_path = Path(r"D:\IVR Case-02\banking-intents-minilm").resolve()
model = AutoModelForSequenceClassification.from_pretrained(str(model_path), local_files_only=True)
tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

def load_label_mapping(model_path):
    with open(model_path / "label2id.json", "r") as f:
        label2id = json.load(f)
    return {str(v): k for k, v in label2id.items()}

id2label = load_label_mapping(model_path)

MAX_CONTEXT_MESSAGES = 12

# Session state stored locally (used alongside Chroma vector context)
session_store = {}

def reset_state(session_id):
    print(f"[reset_state] Resetting session: {session_id}")

    if session_id in session_store:
        del session_store[session_id]
        print(f"[reset_state] Old session deleted: {session_id}")

    session_store[session_id] = {
        "intent": None,
        "stage": None,
        "source": None,
        "destination": None,
        "amount": None,
        "confirmed": False,
    }
    print(f"[reset_state] New session initialized: {session_id} => {session_store[session_id]}")

    # Clear vector context
    collection.delete(where={"session_id": session_id})
    print(f"[reset_state] Vector store context cleared for session: {session_id}")

def get_state(session_id):
    return session_store.get(session_id)

def save_state(session_id, state):
    session_store[session_id] = state

def append_to_history(session_id, sender, text):
    doc_id = f"{session_id}_{sender}_{len(get_recent_context(session_id))}"
    collection.add(
        documents=[f"{sender}: {text}"],
        ids=[doc_id],
        metadatas=[{"session_id": session_id}]
    )

def get_recent_context(session_id):
    results = collection.query(
        query_texts=["context"],
        n_results=MAX_CONTEXT_MESSAGES,
        where={"session_id": session_id}
    )
    return "\n".join([doc for doc in results["documents"][0]])

def sanitize_input(query):
    return re.sub(r'[^a-zA-Z0-9\s]', '', query)

def validate_input(query):
    if not isinstance(query, str) or not query.strip():
        return False, "Query cannot be empty."
    if len(query) > 500:
        return False, "Query is too long."
    return True, ""

def mask_sensitive_data(text):
    return re.sub(r'\d{12,}', '******', text)

def handle_transfer_conversation(session_id, query):
    # Debugging log to track session state access
    logger.info(f"Handling transfer for session: {session_id}")
    
    # Retrieve the session state
    state = get_state(session_id)
    
    # If the state is None, log the issue and initialize the session state for transfer intents
    if state is None:
        logger.warning(f"Session {session_id} not found. Initializing a new session.")
        reset_state(session_id)  # Initialize the session state for this session ID
        state = get_state(session_id)  # Retrieve the newly initialized state
        logger.info(f"New session state initialized: {state}")
    
    append_to_history(session_id, "user", query)  # Append user query to history
    stage = state.get("stage")

    # Handle the transfer process
    if state.get("intent") == "transfer" and stage:
        if stage == "source":
            state["source"] = query.strip()
            state["stage"] = "destination"
            response = "Please provide the destination account."
        elif stage == "destination":
            state["destination"] = query.strip()
            state["stage"] = "amount"
            response = "How much would you like to transfer?"
        elif stage == "amount":
            try:
                amount = float(query.strip().replace("$", "").replace("₹", ""))
                if amount > 10000:
                    response = "Insufficient balance. Please enter a smaller amount."
                else:
                    state["amount"] = amount
                    state["stage"] = "confirm"
                    response = f"Do you confirm the transfer of ₹{amount} from {state['source']} to {state['destination']}?"
            except ValueError:
                response = "Invalid amount. Please enter a valid number."
        elif stage == "confirm":
            if query.strip().lower() in ["yes", "confirm", "y"]:
                summary = f"Transfer ₹{state['amount']} from {state['source']} to {state['destination']}"
                result = transfer_money_tool(summary)
                response = f"{result}"
                reset_state(session_id)  # Reset state after completion
                # Clear history after transfer completion
                collection.delete(where={"session_id": session_id})
                print(f"from line 143 {state.get("intent")}, {state.get("stage")}")
            else:
                response = "Transfer cancelled."
                reset_state(session_id)  # Reset state after cancellation
                # Clear history after cancellation
                collection.delete(where={"session_id": session_id})
        else:
            response = "Sure, from which account would you like to transfer funds?"
            state["stage"] = "source"

        append_to_history(session_id, "bot", response)  # Append bot's response to history
        save_state(session_id, state)
        return response

    # If the intent is not transfer, classify the intent and handle non-transfer cases
    context = get_recent_context(session_id)
    result = classify_intent(query)
    intent = result["intent"]
    confidence = result["confidence"]

    append_to_history(session_id, "user", query)

    # Handle non-transfer queries
    if intent == "transfer" and confidence >= 0.5:
        reset_state(session_id)
        state = get_state(session_id)
        state["intent"] = "transfer"
        state["stage"] = "source"
        save_state(session_id, state)
        response = "Sure, from which account would you like to transfer funds?"
        append_to_history(session_id, "bot", response)
        print(f"from line 175 {state.get("intent")}, {state.get("stage")}")
        return intent, confidence, response

    # Return fallback response for other intents
    fallback = "I'm sorry, I didn't understand that. Could you please rephrase?"
    append_to_history(session_id, "bot", fallback)
    return intent, confidence, fallback

def classify_intent(query, context=""):
    valid, msg = validate_input(query)
    if not valid:
        return {"intent": "fallback", "confidence": 0.0}
    cleaned = sanitize_input(query)
    enriched = f"{context}\n{cleaned}".strip()
    result = classifier(enriched)[0]
    label = result["label"].replace("LABEL_", "")
    confidence = result["score"]
    intent = id2label.get(label, label)
    logger.info(f"Query: {query} | Intent: {intent} | Confidence: {confidence:.2f}")
    return {"intent": intent, "confidence": confidence}

def process_user_query(query, session_id="user-session"):
    state = get_state(session_id)
    if not state:
        reset_state(session_id)
        state = get_state(session_id)

    # Classify current query
    result = classify_intent(query)
    intent = result["intent"]
    confidence = result["confidence"]
    print(f"[Classifier] intent: {intent}, confidence: {confidence}, query: {query}")

    # Check for active intent flow
    if state.get("intent") and state.get("stage"):
        active_intent = state["intent"]

        # Check for cancelation
        if query.lower() in ["cancel", "nevermind", "stop"]:
            reset_state(session_id)
            response = f"{active_intent.capitalize()} cancelled."
            append_to_history(session_id, "bot", response)
            return "cancel", 1.0, response

        # Check if user is switching to a new high-confidence intent
        if intent != active_intent and confidence >= 0.8:
            print(f"[Intent Switch] Switching from {active_intent} to {intent}")
            reset_state(session_id)
            state = get_state(session_id)
            state["intent"] = intent

            if intent == "transfer":
                state["stage"] = "source"
                response = "Sure, from which account would you like to transfer funds?"
            elif intent == "balance":
                response = "Sure, let me check your current balance..."
            else:
                response = f"Intent switched to {intent}. How can I assist?"

            save_state(session_id, state)
            append_to_history(session_id, "bot", response)
            return intent, confidence, response

        # Continue handling current intent (e.g., transfer flow)
        print(f"[Continue Intent] Still handling: {active_intent}")
        return active_intent, 1.0, handle_transfer_conversation(session_id, query)

    # New intent flow starts here (if no prior context or after reset)
    if confidence >= 0.5:
        reset_state(session_id)
        state = get_state(session_id)
        state["intent"] = intent

        if intent == "transfer":
            state["stage"] = "source"
            response = "Sure, from which account would you like to transfer funds?"
        elif intent == "balance":
            response = "Sure, let me check your current balance..."
        else:
            response = f"Intent identified: {intent}. How can I help?"

        save_state(session_id, state)
        append_to_history(session_id, "bot", response)
        return intent, confidence, response

    # Fallback
    fallback = "Low confidence. Please rephrase your query."
    append_to_history(session_id, "bot", fallback)
    return intent, confidence, fallback
