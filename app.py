import os
import traceback
from flask import Flask, render_template, request, jsonify
import httpx
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

app = Flask(__name__)

# Get the API key from environment variables
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("No API key found. Make sure ANTHROPIC_API_KEY is set in your environment variables.")

# Create custom httpx client with headers
http_client = httpx.Client(
    base_url="https://api.anthropic.com",
    headers={
        "anthropic-version": "2023-06-01",
        "x-api-key": api_key,
        "content-type": "application/json"
    }
)

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=api_key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        print("Received chat request")
        data = request.get_json()
        print(f"Request data: {data}")
        
        user_message = data.get('message', '')
        print(f"User message: {user_message}")
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        print("Making request to Anthropic API...")
        try:
            # Direct API call using httpx
            response = http_client.post(
                "/v1/messages",
                json={
                    "model": "claude-2.1",
                    "messages": [{"role": "user", "content": user_message}],
                    "max_tokens": 1000
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result['content'][0]['text']
                return jsonify({'response': answer})
            else:
                print(f"API Error Status: {response.status_code}")
                print(f"API Error Response: {response.text}")
                return jsonify({'error': f'API Error: {response.text}'}), response.status_code
            
        except Exception as api_error:
            print(f"Anthropic API error: {str(api_error)}")
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({'error': f'API Error: {str(api_error)}'}), 500

    except Exception as e:
        print(f"Server error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Server Error: {str(e)}'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': str(error)}), 500

# Create the WSGI application object
application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host=host, port=port, debug=debug)