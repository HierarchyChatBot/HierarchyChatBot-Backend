# server.py

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def llm(input_string):
    # Get characters at odd indices (0-based index: 1, 3, 5, ...)
    return ''.join([input_string[i] for i in range(len(input_string)) if i % 2 == 0])

@app.route('/process-string', methods=['POST'])
def process_string():
    # Get the JSON data from the request
    data = request.json
    input_string = data.get('input_string', '')

    # Process the string
    result = llm(input_string)

    # Return the result as JSON
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True, port=5030)  # Specify the port number here
