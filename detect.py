import os
import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# This allows Lovable to talk to your backend without security blocks
CORS(app, resources={r"/*": {"origins": "https://hexascope.lovable.app"}})

@app.route('/detect', methods=['POST'])
def detect_insect():
    # 1. Get the image from Lovable
    data = request.json
    base64_image = data.get('image')
    
    if not base64_image:
        return jsonify({"error": "No image provided"}), 400

    # 2. Setup OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    openai_url = "https://api.openai.com/v1/chat/completions"

    payload = {
        "model": "gpt-4o-mini",  # Corrected model name
        "max_tokens": 800,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "You are an expert entomologist. Identify this insect and return ONLY a JSON object with keys: common_name, scientific_name, description, habitat, and threat_level."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }]
    }

    try:
        response = requests.post(
            openai_url,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload
        )
        
        # 3. Clean the response
        res_json = response.json()
        raw_content = res_json['choices'][0]['message']['content']
        # Removes markdown backticks if OpenAI adds them
        cleaned = re.sub(r'```json|```', '', raw_content).strip()
        
        # 4. Send back to Lovable
        return cleaned, 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
