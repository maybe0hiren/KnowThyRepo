from flask import Flask, request, jsonify
from pathlib import Path
from flask import render_template


import time
import traceback
import os

from main import indexRepoMain, askMain

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

def logging(repo):
    with open('FILE PATH', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([str(datetime.now()), repo]);



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/indexRepo", methods=["POST"])
def indexRepo():
    ip = request.remote_addr

    if rateLimited(ip):
        return jsonify({"error": "Too many requests"}), 429

    data = request.get_json()
    repoLink = data.get("repoLink")

    if not repoLink:
        return jsonify({"error": "repoLink required"}), 400

    try:
        result = indexRepoMain(repoLink)
        return jsonify({"status": result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": repr(e)}), 500


@app.route("/ask", methods=["POST"])
def ask():
    ip = request.remote_addr

    if rateLimited(ip):
        return jsonify({"error": "Too many requests"}), 429

    data = request.get_json()

    repoLink = data.get("repoLink")

    logging(repoLink)

    question = data.get("question")

    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error": "Missing Authorization header"}), 401

    apiKey = auth.replace("Bearer ", "").strip()

    try:
        answer = askMain(repoLink, question, apiKey)
        return jsonify({"answer": answer})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": repr(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
