from flask import Flask, request, jsonify
from main import main

import time

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


@app.route("/knowThyRepo", methods=["POST"])
def knowThyRepo():
    ip = request.remote_addr

    if rateLimited(ip):
        return jsonify({"error": "Too many requests. Try again later."}), 429

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    repoLink = data.get("repoLink")
    question = data.get("question")

    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return jsonify({"error": "Missing Authorization header"}), 401

    apiKey = auth.replace("Bearer ", "").strip()

    if not repoLink or not question or not apiKey:
        return jsonify({"error": "Required: repoLink, question, apiKey"}), 400

    try:
        answer = main(apiKey, repoLink, question)
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("KnowThyRepo running at http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=True)
