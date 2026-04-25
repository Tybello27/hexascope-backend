import os
import json
import requests
import re
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Pre-flight check for browsers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', 'https://hexascope.lovable.app')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        # 1. SETUP HEADERS
        allowed_origin = "https://hexascope.lovable.app"

        # 2. READ INPUT DATA
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        body = json.loads(post_data)
        base64_image = body.get('image')

        # 3. CALL OPENAI
        api_key = os.environ.get("OPENAI_API_KEY")
        openai_url = "https://api.openai.com/v1/chat/completions"

        payload = {
            "model": "gpt-4.1-mini",
            "max_tokens": 600,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "You are an expert entomologist... (Your full prompt here)"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }]
        }

        try:
            response = requests.post(
                openai_url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload
            )

            res_json = response.json()
            raw_content = res_json['choices'][0]['message']['content']
            cleaned = re.sub(r'```json|```', '', raw_content).strip()

            # 4. SEND RESPONSE
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', allowed_origin)
            self.end_headers()
            self.wfile.write(cleaned.encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))