from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client

app = Flask(__name__)
CORS(app)

# Initialize Gradio client
hf_client = Client("Ayingxizhao/contentguard-model")

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        text = data.get('content', '')
        
        if not text:
            return jsonify({"error": "No content provided"}), 400
        
        # Call your HF Space
        result = hf_client.predict(text=text, api_name="/predict")
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)