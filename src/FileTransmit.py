# FileTransmit.py

from flask import Blueprint, request, jsonify, send_file
import os
import zipfile
import io
from datetime import datetime
import json

file_transmit_bp = Blueprint('file_transmit', __name__)

# Define the workspace directory
WORKSPACE_FOLDER = './'
if not os.path.exists(WORKSPACE_FOLDER):
    os.makedirs(WORKSPACE_FOLDER)

# Route to handle file uploads
@file_transmit_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files selected for uploading'}), 400

    for file in files:
        if file.filename == '':
            continue
        file.save(os.path.join(WORKSPACE_FOLDER, file.filename))
        print(f"upload file: {file.filename}")
    return jsonify({'message': 'Files successfully uploaded'}), 200

# Route to handle downloading the workspace as a zip file
@file_transmit_bp.route('/download', methods=['GET'])
def download_workspace():
    zip_filename = f'workspace_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_STORED) as zip_file:
        for root, dirs, files in os.walk(WORKSPACE_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, WORKSPACE_FOLDER)
                zip_file.write(file_path, arcname)

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name=zip_filename, mimetype='application/zip')

# New route to handle saving graph data as JSON
@file_transmit_bp.route('/save-graph', methods=['POST'])
def save_graph():
    try:
        # Parse the incoming JSON data
        graph_data = request.get_json()

        if not graph_data:
            return jsonify({'error': 'No graph data provided'}), 400

        # Save the JSON data to a file in the workspace
        graph_file_path = os.path.join(WORKSPACE_FOLDER, 'graph.json')
        with open(graph_file_path, 'w') as graph_file:
            json.dump(graph_data, graph_file, indent=2)

        print(f"Graph data saved to {graph_file_path}")
        return jsonify({'message': 'Graph data successfully saved'}), 200

    except Exception as e:
        print(f"Error saving graph data: {e}")
        return jsonify({'error': f"Failed to save graph data: {str(e)}"}), 500

# New route to handle cleaning the workspace (deleting all files)
@file_transmit_bp.route('/clean-cache', methods=['POST'])
def clean_cache():
    try:
        # Loop through all files in the workspace and delete them
        for root, dirs, files in os.walk(WORKSPACE_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        return jsonify({'message': 'Workspace successfully cleaned'}), 200
    except Exception as e:
        print(f"Error cleaning workspace: {e}")
        return jsonify({'error': f"Failed to clean workspace: {str(e)}"}), 500
