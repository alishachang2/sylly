from flask import Flask, request, jsonify, send_file
import os
import sys

app = Flask(__name__)

@app.route("/")
def calendar_ics():
    file_path = "./test_file/dummy_multiple.ics"
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name="Calendar.ics")
    else:
        return "Parse failed", 404


    