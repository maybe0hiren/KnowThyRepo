from flask import Flask, request, jsonify
from pathlib import Path
from flask import render_template
from datetime import datetime
import csv
import time
import traceback
import os

import sqlDB
from main import main

sqlDB.createTable()
app = Flask(__name__)

RATE_LIMIT = 5
WINDOW_SECONDS = 60
ip_requests = {}

def rateLimited(ip: str) -> bool:
    now = time.time()

    if ip not in ip_requests:
        ip_requests[ip] = []

    ip_requests[ip] = [t for t in ip_requests[ip] if now - t < WINDOW_SECONDS]

    if len(ip_requests[ip]) >= RATE_LIMIT:
        return True

    ip_requests[ip].append(now)
    return False

def logging(repo, timeTaken, status):
    with open('FILE', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([str(datetime.now()), repo, str(timeTaken), status]);



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def askQuestion():
    repoLink = "None"
    timeStart = time.perf_counter()
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        traceback.print_exc()
        timeTaken = int((time.perf_counter() - timeStart) * 1000)
        logging(repoLink, timeTaken, "Failed - Unauthorized")
        return jsonify({"error": "Missing Authorization header"}), 401

    ip = request.remote_addr
    if rateLimited(ip):
        traceback.print_exc()
        timeTaken = int((time.perf_counter() - timeStart) * 1000)
        logging(repoLink, timeTaken, "Failed - RequestLimit")
        return jsonify({"error": "Too many requests"}), 429

    data = request.get_json()
    repoLink = data.get("repoLink")
    if not repoLink:
        traceback.print_exc()
        timeTaken = int((time.perf_counter() - timeStart) * 1000)
        logging(repoLink, timeTaken, "Failed - Missing Repo")
        return jsonify({"error": "repoLink required"}), 400
    question = data.get("question")
    if not question:
        traceback.print_exc()
        timeTaken = int((time.perf_counter() - timeStart) * 1000)
        logging(repoLink, timeTaken, "Failed - Missing Question")
        return jsonify({"error": "Question required"}), 400
    apiKey = auth.replace("Bearer ", "").strip()

    try:
        answer = main(repoLink, question, apiKey)
        timeTaken = int((time.perf_counter() - timeStart) * 1000)
        logging(repoLink, timeTaken, "Success")
        return jsonify({"answer": answer})
    except Exception as e:
        traceback.print_exc()
        timeTaken = int((time.perf_counter() - timeStart) * 1000)
        logging(repoLink, timeTaken, "Failed - Execution error")
        return jsonify({"error": repr(e)}), 500

    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
