import json
import logging
import re
from pathlib import Path
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Set up logging
logging.basicConfig(level=logging.INFO, filename='intent_classifier.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Model path
model_path = Path(r"D:\IVR Case-02\banking-intents-minilm").resolve()

# Check model directory
if not model_path.exists():
    raise FileNotFoundError(f"Model directory does not exist: {model_path}")

logger.info(f"Model directory contents: {[p.name for p in model_path.iterdir()]}")

# Utility Functions
def sanitize_input(query):
    return re.sub(r'[^a-zA-Z0-9\s]', '', query)

def validate_input(query):
    if not isinstance(query, str) or not query.strip():
        return False, "Query cannot be empty."
    if len(query) > 500:
        return False, "Query is too long. Please keep it under 500 characters."
    return True, ""

def mask_sensitive_data(text):
    return re.sub(r'\d{12,}', '******', text)

def log_query_response(query, intent, confidence):
    logger.info(f"Query: {query} | Predicted Intent: {intent} | Confidence: {confidence:.2f}")

# Load label mapping
def load_label_mapping(model_path):
    label2id_path = model_path / "label2id.json"
    try:
        with open(label2id_path, "r") as f:
            label2id = json.load(f)
        id2label = {str(v): k for k, v in label2id.items()}
        logger.info(f"Label mapping: {id2label}")
        return id2label
    except FileNotFoundError:
        logger.warning(f"label2id.json not found at {label2id_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding label2id.json")
        return {}

# Load model and tokenizer
try:
    logger.info("Loading model and tokenizer")
    model = AutoModelForSequenceClassification.from_pretrained(str(model_path), local_files_only=True)
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
except Exception as e:
    logger.error(f"Model load error: {e}")
    raise Exception(f"Error loading model/tokenizer: {e}")

# Load label mapping
id2label = load_label_mapping(model_path)
if not id2label:
    logger.warning("No label mapping. Using LABEL_X.")

# Initialize pipeline
try:
    logger.info("Initializing pipeline")
    classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)
except Exception as e:
    logger.error(f"Pipeline error: {e}")
    raise Exception(f"Error initializing pipeline: {e}")

def classify_intent(query):
    """
    Classify the intent of a given query.
    Args:
        query (str): Input text to classify.
    Returns:
        dict: Intent and confidence score.
    """
    is_valid, validation_msg = validate_input(query)
    if not is_valid:
        logger.info(f"Validation failed: {validation_msg}")
        return {"intent": "fallback", "confidence": 0.0}

    sanitized_query = sanitize_input(query)

    try:
        logger.info(f"Classifying: '{sanitized_query}'")
        result = classifier(sanitized_query)
        logger.info(f"Classifier output: {result}")

        label = result[0]["label"]
        confidence = result[0]["score"]

        intent = id2label.get(label.replace("LABEL_", ""), label) if id2label else label

        log_query_response(sanitized_query, intent, confidence)

        if confidence < 0.5:
            logger.info(f"Low confidence {confidence} for {intent}; using fallback")
            return {"intent": "fallback", "confidence": float(confidence)}

        return {"intent": mask_sensitive_data(intent), "confidence": float(confidence)}
    except Exception as e:
        logger.error(f"Classification error: {e}")
        return {"intent": "fallback", "confidence": 0.0}

def process_user_query(query):
    result = classify_intent(query)
    intent = result["intent"]
    confidence = result["confidence"]

    if intent != "fallback":
        return intent, confidence, "Intent recognized successfully."
    else:
        return intent, confidence, "Low confidence. Please rephrase your query."

# CLI test
if __name__ == "__main__":
    test_queries = [
        "What is my account balance?",
        "Check my account balance",
        "Track my mortgage payments",
        "Transfer money to 1234567890123456",
        "How do I block my lost card?",
        "Can I make a payment?",
        "Show my recent transactions"
    ]
    for query in test_queries:
        intent, confidence, response = process_user_query(query)
        print(f"Query: '{query}' -> Intent: {intent}, Confidence: {confidence:.2f}, Response: {response}")
