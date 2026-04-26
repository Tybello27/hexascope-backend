import os
import requests
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/detect', methods=['POST'])
def detect_insect():
    data = request.json
    base64_image = data.get('image')

    if not base64_image:
        return jsonify({"error": "No image provided"}), 400

    # Handle both cases - with or without prefix
    if not base64_image.startswith('data:image'):
        base64_image = f"data:image/jpeg;base64,{base64_image}"

    api_key = os.environ.get("OPENAI_API_KEY")
    openai_url = "https://api.openai.com/v1/chat/completions"

    payload = {
        "model": "gpt-4o-mini",
        "max_tokens": 1000,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """You are an expert entomologist. Identify the insect in this image and return ONLY a raw JSON object. No markdown, no backticks, just JSON. Every field is mandatory, never leave any field empty or null. Return exactly these fields:
{
  "insect_name": "common name",
  "biological_name": "full scientific name",
  "genus": "genus only",
  "species": "species only",
  "classification": {
    "kingdom": "Animalia",
    "phylum": "Arthropoda",
    "class": "Insecta",
    "order": "fill this",
    "family": "fill this",
    "genus": "fill this",
    "species": "fill this"
  },
  "confidence": 0.95,
  "danger_level": "low or medium or high",
  "school_risk_level": "low or medium or high",
  "diet": "what it eats",
  "lifespan": "average lifespan",
  "habitat": "where it lives",
  "population": "how widespread it is",
  "economic_importance": "2-3 sentences on economic impact",
  "bio": "2-3 sentences on characteristics and behaviour"
}"""
                },
                {
                    "type": "image_url",
                    "image_url": {"url": base64_image}
                }
            ]
        }]
    }

    try:
        response = requests.post(
            openai_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload
        )

        res_json = response.json()
        raw_content = res_json['choices'][0]['message']['content']
        cleaned = re.sub(r'```json|```', '', raw_content).strip()
        result = json.loads(cleaned)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e), "raw": res_json if 'res_json' in locals() else "no response"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
