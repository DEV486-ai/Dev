from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)

# Gemini API Setup
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise Exception("GEMINI_API_KEY missing")

client = genai.Client(
    api_key=API_KEY
)


# MongoDB Optional Setup
chat_collection = None

MONGO_URI = os.environ.get("MONGO_URI")

if MONGO_URI:
    try:
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client["bongbrowser"]
        chat_collection = db["chat_history"]
        print("MongoDB Connected")
    except Exception as e:
        print("MongoDB Error:", e)


@app.route("/")
def home():
    return jsonify({
        "message": "BongBrowser AI Backend is Running"
    })


@app.route("/api/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data received"
            }), 400


        message = data.get("message", "")
        language = data.get("language", "English")


        if not message:
            return jsonify({
                "success": False,
                "error": "Message empty"
            }), 400


        prompt = f"""
You are BongBrowser AI Assistant.

Answer language:
{language}

User:
{message}

Give a helpful answer.
"""


        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )


        reply = response.text


        # Save chat only if MongoDB exists
        if chat_collection:
            chat_collection.insert_one({
                "message": message,
                "language": language,
                "reply": reply
            })


        return jsonify({
            "success": True,
            "reply": reply
        })


    except Exception as e:

        print("AI ERROR:", e)

        return jsonify({
            "success": False,
            "error": str(e)
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
