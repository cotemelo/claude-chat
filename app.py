import os
import traceback
from flask import Flask, render_template, request, jsonify
from anthropic import Anthropic

app = Flask(__name__)

# Get the API key from environment variables
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("No API key found. Make sure ANTHROPIC_API_KEY is set in your environment variables.")

# Initialize Anthropic client
anthropic_client = Anthropic(
    api_key=api_key,
    base_url="https://api.anthropic.com",
    default_headers={
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
)

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
            # Using the messages API instead of completions
            message = anthropic_client.messages.create(
                model="claude-2.1",
                messages=[{
                    "role": "user",
                    "content": user_message
                }],
                max_tokens=1000
            )
            print(f"Received response: {message}")
            
            # Extract the response text
            response_text = message.content[0].text
            return jsonify({'response': response_text})
            
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