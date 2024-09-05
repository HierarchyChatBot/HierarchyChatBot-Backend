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

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


llm_model = "gpt4"
open_ai_key = ""

@app.route('/process-string', methods=['POST'])
def process_string():
    # Get the JSON data from the request
    data = request.json
    input_string = data.get('input_string', '')

    # Process the string
    result = ChatBot(get_llm(llm_model, open_ai_key), input_string)

    # Return the result as JSON
    return jsonify({'result': result})

app.register_blueprint(file_transmit_bp)  # Register the Blueprint

server_tee = ServerTee("server.log")
thread_handler = ThreadHandler.get_instance()

def server_func():
    try:
        run_workflow_as_server(get_llm(llm_model, open_ai_key))
    except Exception as e:
        print(str(e))
        raise

@app.route('/run', methods=['POST'])
def run_script():
    if thread_handler.is_running():
        return "Another instance is already running", 409

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
    if thread_handler.is_running():
        thread_handler.force_reset()
        return "Script stopped", 200
    else:
        return "No script is running", 400

@app.route('/status', methods=['GET'])
def check_status():
    running = thread_handler.is_running()
    return jsonify({"running": running}), 200

@app.route('/config', methods=['GET'])
def get_config():
    # Send the current LLM model and OpenAI key to the frontend
    return jsonify({
        'llm_model': llm_model,
        'open_ai_key': open_ai_key
    }), 200

@app.route('/config', methods=['POST'])
def config():
    global llm_model, open_ai_key  # Declare the global variables
    
    # Get the JSON data sent from the frontend
    config_data = request.get_json()

    # Update the global variables with the new configuration
    llm_model = config_data.get('llm_model')
    open_ai_key = config_data.get('open_ai_key')

    # Print the configuration data to the console
    print("Received Configuration Data: ", config_data)

    # Send a response back to the frontend
    return jsonify({"message": "Configuration settings saved successfully!"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5030)  # Specify the port number here
