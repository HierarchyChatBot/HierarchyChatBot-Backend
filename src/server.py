# server.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from llm import ChatBot, get_llm
from flask import Flask, Response, stream_with_context, request, jsonify
import os
from ServerTee import ServerTee
from thread_handler import ThreadHandler
from WorkFlow import run_workflow_as_server
from FileTransmit import file_transmit_bp  # Import the Blueprint
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to get the current log file path
def get_log_file_path():
    log_dir = os.path.join(os.path.dirname(__file__), '../log')  # Ensure the path is correct
    os.makedirs(log_dir, exist_ok=True)  # Create the log directory if it doesn't exist
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_file = f'{current_date}.log'
    return os.path.join("/app/src/log/", log_file)

server_tee = ServerTee(get_log_file_path())
thread_handler = ThreadHandler.get_instance()

# Print the log file path for reference
print(get_log_file_path())

@app.route('/process-string', methods=['POST'])
def process_string():
    # Get the JSON data from the request
    data = request.json
    input_string = data.get('input_string', '')
    llm_model = data.get('llm_model', 'gemma2')  # Default to 'gpt' if not provided
    open_ai_key = data.get('open_ai_key', '')

    # Process the string using the dynamically provided llm_model and open_ai_key
    result = ChatBot(get_llm(llm_model, open_ai_key), input_string)

    # Return the result as JSON
    return jsonify({'result': result})

@app.route('/run', methods=['POST'])
def run_script():
    # Get llm_model and open_ai_key from the request body
    data = request.json
    llm_model = data.get('llm_model', 'gemma2')  # Default to 'gpt' if not provided
    open_ai_key = data.get('open_ai_key', '')

    if thread_handler.is_running():
        return "Another instance is already running", 409

    def server_func():
        try:
            # Run the workflow using the provided llm_model and open_ai_key
            run_workflow_as_server(get_llm(llm_model, open_ai_key))
        except Exception as e:
            print(str(e))
            raise

    def generate():
        try:
            thread_handler.start_thread(target=server_func)
            yield from server_tee.stream_to_frontend()
        except Exception as e:
            print(str(e))
            yield "Error occurred: " + str(e)
        finally:
            if not thread_handler.is_running():
                yield "finished"

    return Response(stream_with_context(generate()), content_type='text/plain; charset=utf-8')

@app.route('/stop', methods=['POST'])
def stop_script():
    try:
        # Example restart request (modify as needed)
        response = requests.get('http://ollama:11435/restart')
        if response.status_code == 200:
            return "Script stopped and restart request sent", 200
        else:
            return f"Script stopped, but restart request failed with status code {response.status_code}", 500
    except requests.RequestException as e:
        return f"Script stopped, but failed to send restart request: {str(e)}", 500

    if thread_handler.is_running():
        thread_handler.force_reset()
        return "Script stopped", 200
    else:
        return "No script is running", 400

@app.route('/status', methods=['GET'])
def check_status():
    running = thread_handler.is_running()
    return jsonify({"running": running}), 200

app.register_blueprint(file_transmit_bp)  # Register the Blueprint

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5030)  # Specify the port number here
