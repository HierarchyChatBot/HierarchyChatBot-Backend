# server.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from llm import ChatBot

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/process-string', methods=['POST'])
def process_string():
    # Get the JSON data from the request
    data = request.json
    input_string = data.get('input_string', '')

    # Process the string
    result = ChatBot(input_string)

    # Return the result as JSON
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True, port=5030)  # Specify the port number here
