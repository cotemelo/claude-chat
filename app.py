import os
from flask import Flask, render_template, request, jsonify
import anthropic

app = Flask(__name__)

# Get the API key from environment variables
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("No API key found. Make sure ANTHROPIC_API_KEY is set in your environment variables.")

# Initialize Anthropic client with just the API key
c = anthropic.Client(api_key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Create a completion with minimal parameters
        response = c.completion(
            prompt=f"{anthropic.HUMAN_PROMPT} {user_message}{anthropic.AI_PROMPT}",
            model="claude-3-opus-20240229",
            max_tokens_to_sample=1000,
        )

        return jsonify({'response': response.completion})

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500

# Create the WSGI application object
application = app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host=host, port=port, debug=debug)