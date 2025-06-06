import os
from flask import Flask, request, jsonify
from kiddylang import run_jam_code
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

@app.route("/run", methods=["POST"])
def run_code():
    data = request.json
    code = data.get("code", "")
    result = run_jam_code(code)
    return jsonify({"output": result})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
