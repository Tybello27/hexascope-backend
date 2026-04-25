# Hexascope AI - Insect Identification Backend

This is the Python-based AI processing engine for the Hexascope project. It handles image processing and integrates with OpenAI's Vision API to identify insects and provide detailed biological data.

## Features
- **AI Identification:** Uses GPT-4o-mini to analyze insect images.
- **REST API:** Built with Flask for high-performance connectivity.
- **CORS Enabled:** Securely connects with the Lovable frontend.

## Tech Stack
- Python 3.12+
- Flask
- OpenAI Vision API
- Hosted on Render (Frankfurt Region)

## Deployment Instructions
1. Ensure `OPENAI_API_KEY` is set in the environment variables.
2. Run `pip install -r requirements.txt`.
3. Start the server using `gunicorn detect:app`.

