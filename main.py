import os
import requests
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UNKNOWN_RESPONSE = {
    "insect_name": "Unknown Insect",
    "biological_name": "Unknown",
    "genus": "Unknown",
    "species": "Unknown",
    "classification": {
        "kingdom": "Unknown",
        "phylum": "Unknown",
        "class": "Unknown",
        "order": "Unknown",
        "family": "Unknown",
        "genus": "Unknown",
        "species": "Unknown"
    },
    "confidence": 0,
    "danger_level": "unknown",
    "school_risk_level": "unknown",
    "diet": "Unknown",
    "lifespan": "Unknown",
    "habitat": "Unknown",
    "population": "Unknown",
    "economic_importance": "Unable to determine.",
    "bio": "Unable to process the image. Please try again."
}

@app.route('/detect', methods=['POST'])
def detect_insect():
    data = request.json
    base64_image = data.get('image')

@app.route('/debug', methods=['POST'])
def debug():
    data = request.json
    image = data.get('image', '')
    return jsonify({
        "received": True,
        "image_length": len(image),
        "starts_with": image[:50] if image else "empty",
        "has_prefix": image.startswith('data:image') if image else False
    }), 200
    

    if not base64_image:
        response = UNKNOWN_RESPONSE.copy()
        response["insect_name"] = "No Image"
        response["bio"] = "No image was provided. Please upload a photo of an insect."
        return jsonify(response), 200

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
                    "text": """You are an expert entomologist with advanced image analysis capabilities. Identify the insect in this image.

IMPORTANT RULES ABOUT IMAGE QUALITY:
- Accept ALL real-world photos including phone camera shots, outdoor photos, indoor photos, close-ups, and slightly blurry images
- Do NOT reject an image just because it is not perfect quality
- Do NOT complain about image size, resolution, or file format
- Make your best identification even from imperfect photos — this is what field entomologists do
- Only return Unknown Insect if the insect is genuinely impossible to identify after your best effort

IMPORTANT RULES ABOUT IDENTIFICATION:
1. If the image does not contain an insect at all, or contains a human, food, object or scenery — set insect_name to "No Insect Detected" and bio to "No insect was found in this image. Please upload a clear photo of an insect."

2. If you genuinely cannot identify the insect even after your best effort due to extreme blurriness or darkness — set insect_name to "Unknown Insect" and bio to "The image is not clear enough for identification. Please take a closer photo in good lighting with the insect centered in the frame."

3. For ALL real photos including phone camera shots, outdoor snaps, and close-ups — make your best identification and fill in ALL fields completely and accurately. Never leave any field as null or empty.

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
            error_response = UNKNOWN_RESPONSE.copy()
            error_response["insect_name"] = "Connection Issue"
            error_response["bio"] = "The AI is currently busy. Please try again in a moment."
            return jsonify(error_response), 200

        raw_content = res_json['choices'][0]['message']['content']
        cleaned = re.sub(r'```json|```', '', raw_content).strip()
        result = json.loads(cleaned)

        return jsonify(result), 200

    except requests.exceptions.Timeout:
        timeout_response = UNKNOWN_RESPONSE.copy()
        timeout_response["insect_name"] = "Request Timed Out"
        timeout_response["bio"] = "The request took too long. Please try again with a smaller or clearer image."
        return jsonify(timeout_response), 200

    except Exception as e:
        error_response = UNKNOWN_RESPONSE.copy()
        error_response["insect_name"] = "Image Unclear"
        error_response["bio"] = "I couldn't quite make that out. Please ensure the insect is centered and well-lit."
        return jsonify(error_response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
