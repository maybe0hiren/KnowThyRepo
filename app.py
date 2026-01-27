from flask import Flask, request, jsonify
from main import main

app = Flask(__name__)


@app.route("/knowThyRepo", methods=["POST"])
def know_thy_repo():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    projectPath = data.get("projectPath")
    question = data.get("question")
    apiKey = data.get("apiKey")

    if not all([projectPath, question, apiKey]):
        return jsonify({
            "error": "Required fields: projectPath, question, apiKey"
        }), 400

    try:
        result = main(apiKey, projectPath, question)
        return jsonify({"answer": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
