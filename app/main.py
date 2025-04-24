from flask import Flask, request, jsonify
from app.nlp import process_user_query  # Function to classify intent
from app.router import AutoGenRouter
from app.log_util import log_query_response

app = Flask(__name__)

router = AutoGenRouter()

CONFIDENCE_THRESHOLD = 0.5  # Must match the threshold in your nlp.py

@app.route("/predict_intent", methods=["POST"])
def predict_intent():
    data = request.json
    query = data.get("query")
    session_id = data.get("session_id", "user-session")  # Retrieve session_id or use default

    if not query:
        return jsonify({"error": "Query is required"}), 400

    # Step 1: Classify the query
    intent, confidence, action_response = process_user_query(query, session_id)

    # Step 2: Route to tool if confidence is high
    if confidence >= CONFIDENCE_THRESHOLD:
        final_response = router.route(query, intent, confidence)
    else:
        final_response = action_response  # fallback response

    # Step 3: Log and return the result
    log_query_response(query, intent, final_response, confidence)

    return jsonify({
        "query": query,
        "intent": intent,
        "confidence": confidence,
        "response": final_response
    })

if __name__ == "__main__":
    app.run(debug=True)
