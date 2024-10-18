from flask import Flask, request, jsonify
from flask_cors import CORS
from models.model import probe_model_5l_profit
import json
from datetime import datetime

app = Flask(__name__)
# Allow all CORS requests
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})


@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    # Check if file exists in request
    if 'file' not in request.files:
        return jsonify({
            'error': 'No file provided',
            'message': 'Please upload a JSON file'
        }), 400
    
    file = request.files['file']
    
    # Check if file name is empty
    if file.filename == '':
        return jsonify({
            'error': 'No file selected',
            'message': 'Please select a file to upload'
        }), 400
    
    # Check file extension
    if not file.filename.endswith('.json'):
        return jsonify({
            'error': 'Invalid file type',
            'message': 'Please upload a JSON file'
        }), 400
    
    try:
        # Load and validate JSON data
        data = json.load(file)
        
        if "data" not in data:
            raise KeyError("Missing 'data' key in JSON file")
            
        # Process the data using the model
        result = probe_model_5l_profit(data["data"])
        
        # Add metadata to the response
        response = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "data_version": "1.0",
                "filename": file.filename
            },
            **result  # This will include the flags from your model
        }
        
        return jsonify(response)
        
    except json.JSONDecodeError:
        return jsonify({
            'error': 'Invalid JSON',
            'message': 'The uploaded file is not a valid JSON file'
        }), 400
    except KeyError as e:
        return jsonify({
            'error': 'Invalid data structure',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Processing error',
            'message': str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
