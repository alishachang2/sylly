from flask import Flask, request, jsonify
import os
from fixed_parse import extract_pdf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/file", methods=["POST"])
def parse():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]

    saved_path = "uploaded.pdf"
    file.save(saved_path)

    try:
        result = extract_pdf(saved_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
