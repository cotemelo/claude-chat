import os
import traceback
from flask import Flask, render_template, request, jsonify
import anthropic
from anthropic.api import API_VERSION

app = Flask(__name__)

# Get the API key from environment variables
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("No API key found. Make sure ANTHROPIC_API_KEY is set in your environment variables.")

# Initialize Anthropic client with version header
c = anthropic.Client(
    api_key,
    default_headers={"anthropic-version": "2023-06-01"}  # Adding required version header
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
            # Create a completion with minimal parameters
            response = c.completion(
                prompt=f"{anthropic.HUMAN_PROMPT} {user_message}{anthropic.AI_PROMPT}",
                model="claude-2.1",
                max_tokens_to_sample=1000,
                temperature=0.7,
                stop_sequences=[anthropic.HUMAN_PROMPT]
            )
            print(f"Received response: {response}")
            
            return jsonify({'response': response.completion})
            
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