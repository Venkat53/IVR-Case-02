from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/balance', methods=['POST'])
def check_balance():
    data = request.get_json()
    query = data.get("query", "")
    return jsonify({"message": "Your current balance is $1,234.56."})

@app.route('/transfer', methods=['POST'])
def transfer_money():
    data = request.get_json()
    query = data.get("query", "")
    return jsonify({"message": "Money transfer has been successfully initiated."})

@app.route('/report-fraud', methods=['POST'])
def report_fraud():
    data = request.get_json()
    query = data.get("query", "")
    return jsonify({"message": "Fraud reported successfully. Our team will contact you shortly."})

@app.route('/open-account', methods=['POST'])
def open_account():
    data = request.get_json()
    query = data.get("query", "")
    return jsonify({"message": "An account opening link has been sent to your registered email."})

@app.route('/loan-status', methods=['POST'])
def loan_status():
    data = request.get_json()
    query = data.get("query", "")
    return jsonify({"message": "Your loan application is under review and will be approved in 3 days."})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
