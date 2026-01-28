from flask import Flask, request, jsonify
from main import main

app = Flask(__name__)


@app.route("/knowThyRepo", methods=["POST"])
def know_thy_repo():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    repoLink = data.get("repoLink")
    question = data.get("question")
    apiKey = data.get("apiKey")

    if not all([repoLink, question, apiKey]):
        return jsonify({
            "error": "Required fields: repoLink, question, apiKey"
        }), 400

    try:
        answer = main(apiKey, repoLink, question)
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("KnowThyRepo backend running on http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=True)
