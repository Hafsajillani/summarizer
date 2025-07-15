from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app)  # This will allow all origins by default

GEMINI_API_KEY = "AIzaSyAzI5YCoEPQ1yxPmYGqH8PD4MZwDYNzGZU"  # Hardcoded for testing
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    return " ".join(paragraphs)

@app.route("/")
def home():
    return "Flask server is running!"

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Fetch article HTML
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"Error fetching article: {e}")
        return jsonify({"error": f"Failed to fetch article: {str(e)}"}), 500

    # Extract text
    article_text = extract_text_from_html(html)
    if not article_text:
        print("Could not extract article text")
        return jsonify({"error": "Could not extract article text"}), 500

    # Send to Gemini
    payload = {
        "contents": [{"parts": [{"text": article_text}]}]
    }
    try:
        gemini_resp = requests.post(
            GEMINI_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        gemini_resp.raise_for_status()
        gemini_data = gemini_resp.json()
        summary = (
            gemini_data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )
        return jsonify({"summary": summary})
    except Exception as e:
        print(f"Error from Gemini API: {e}")
        return jsonify({"error": f"Gemini API error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
