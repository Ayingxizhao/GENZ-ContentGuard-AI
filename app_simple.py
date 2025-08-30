from flask import Flask, render_template, request, jsonify
import os
from local_model import analyze_with_local_model, local_detector
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        title = data.get('title', '')
        content = data.get('content', '')
        use_openai = data.get('use_openai', False)
        
        if not title and not content:
            return jsonify({'error': 'Please provide either a title or content to analyze'}), 400
        
        # Use local model (OpenAI disabled for now due to dependency issues)
        result = analyze_with_local_model(title, content)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'analysis': result['analysis'],
            'is_malicious': result['is_malicious'],
            'confidence': result['confidence'],
            'model_type': result['model_type'],
            'probabilities': result['probabilities'],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/model-info')
def model_info():
    """Get information about available models"""
    return jsonify({
        'local_model': local_detector.get_model_info(),
        'openai_available': False  # Disabled due to dependency issues
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
