import logging
from datetime import datetime

logging.basicConfig(
    filename='ivr_logs.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def log_query_response(query, intent, response, confidence):
    logging.info(f"Query: {query} | Intent: {intent} | Confidence: {confidence:.2f} | Response: {response}")
