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
        return jsonify({
            "insect_name": "No Image",
            "biological_name": "Unknown",
            "genus": "Unknown",
            "species": "Unknown",
            "classification": {"kingdom": "Unknown", "phylum": "Unknown", "class": "Unknown", "order": "Unknown", "family": "Unknown", "genus": "Unknown", "species": "Unknown"},
            "confidence": 0,
            "danger_level": "unknown",
            "school_risk_level": "unknown",
            "diet": "Unknown",
            "lifespan": "Unknown",
            "habitat": "Unknown",
            "population": "Unknown",
            "economic_importance": "Unable to determine.",
            "bio": "No image was provided. Please upload a photo of an insect."
        }), 200

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
                    "text": """You are an expert entomologist. Identify the insect in this image.

IMPORTANT RULES:
1. If the image does not contain an insect at all, or contains a human, food, object or scenery — set insect_name to "No Insect Detected" and bio to "No insect was found in this image. Please upload a clear photo of an insect."

2. If the image contains an insect but is too blurry, too dark, too far away, or the insect is too small to identify confidently — set insect_name to "Unknown Insect" and bio to "The image is not clear enough for identification. Please take a closer photo in good lighting with the insect centered in the frame."

3. If the insect is clearly visible and identifiable — fill in ALL fields completely and accurately. Never leave any field as null or empty.

In ALL cases return ONLY this raw JSON structure with no markdown and no backticks:
{
  "insect_name": "common name or Unknown Insect or No Insect Detected",
  "biological_name": "full scientific name or Unknown",
  "genus": "genus or Unknown",
  "species": "species or Unknown",
  "classification": {
    "kingdom": "Animalia or Unknown",
    "phylum": "Arthropoda or Unknown",
    "class": "Insecta or Unknown",
    "order": "fill or Unknown",
    "family": "fill or Unknown",
    "genus": "fill or Unknown",
    "species": "fill or Unknown"
  },
  "confidence": 0.95,
  "danger_level": "low or medium or high or unknown",
  "school_risk_level": "low or medium or high or unknown",
  "diet": "what it eats or Unknown",
  "lifespan": "average lifespan or Unknown",
  "habitat": "where it lives or Unknown",
  "population": "how widespread or Unknown",
  "economic_importance": "economic impact or Unable to determine",
  "bio": "description or reason why identification failed"
}"""
                },
                {
                    "type": "image_url",
                    "image_url": {"url": base64_image}
                }
            ]
        }]
    }

    res_json = None
    try:
        response = requests.post(
            openai_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )

        res_json = response.json()

        if "error" in res_json:
            return jsonify({
                "insect_name": "Connection Issue",
                "biological_name": "Unknown",
                "genus": "Unknown",
                "species": "Unknown",
                "classification": {"kingdom": "Unknown", "phylum": "Unknown", "class": "Unknown", "order": "Unknown", "family": "Unknown", "genus": "Unknown", "species": "Unknown"},
                "confidence": 0,
                "danger_level": "unknown",
                "school_risk_level": "unknown",
                "diet": "Unknown",
                "lifespan": "Unknown",
                "habitat": "Unknown",
                "population": "Unknown",
                "economic_importance": "Unable to determine.",
                "bio": "The AI is currently busy. Please try again in a moment."
            }), 200

        raw_content = res_json['choices'][0]['message']['content']
        cleaned = re.sub(r'```json|```', '', raw_content).strip()
        result = json.loads(cleaned)

        return jsonify(result), 200

    except requests.exceptions.Timeout:
        return jsonify({
            "insect_name": "Request Timed Out",
            "biological_name": "Unknown",
            "genus": "Unknown",
            "species": "Unknown",
            "classification": {"kingdom": "Unknown", "phylum": "Unknown", "class": "Unknown", "order": "Unknown", "family": "Unknown", "genus": "Unknown", "species": "Unknown"},
            "confidence": 0,
            "danger_level": "unknown",
            "school_risk_level": "unknown",
            "diet": "Unknown",
            "lifespan": "Unknown",
            "habitat": "Unknown",
            "population": "Unknown",
            "economic_importance": "Unable to determine.",
            "bio": "The request took too long. Please try again with a smaller or clearer image."
        }), 200

    except Exception as e:
        return jsonify({
            "insect_name": "Image Unclear",
            "biological_name": "Unknown",
            "genus": "Unknown",
            "species": "Unknown",
            "classification": {"kingdom": "Unknown", "phylum": "Unknown", "class": "Unknown", "order": "Unknown", "family": "Unknown", "genus": "Unknown", "species": "Unknown"},
            "confidence": 0,
            "danger_level": "unknown",
            "school_risk_level": "unknown",
            "diet": "Unknown",
            "lifespan": "Unknown",
            "habitat": "Unknown",
            "population": "Unknown",
            "economic_importance": "Unable to determine.",
            "bio": "I couldn't quite make that out. Please ensure the insect is centered and well-lit."
        }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
