from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
import os

app = Flask(__name__)

CORS(app)

# Gemini API connection
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


@app.route("/")
def home():
    return jsonify({
        "message": "BongBrowser AI Backend is Running"
    })


@app.route("/api/chat", methods=["POST"])
def chat():

    try:
        data = request.json

        message = data.get("message", "")
        language = data.get("language", "English")

        prompt = f"""
You are BongBrowser AI Assistant.

Reply language:
{language}

User message:
{message}

Give a helpful and accurate answer.
"""

        result = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return jsonify({
            "success": True,
            "reply": result.text
        })


    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/api/health")
def health():

    return jsonify({
        "status": "BongBrowser AI OK"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
)
