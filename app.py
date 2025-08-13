from flask import Flask, render_template, request, jsonify
import os
from llm import analyze_post_content
import time
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        title = data.get('title', '')
        content = data.get('content', '')
        
        if not title and not content:
            return jsonify({'error': 'Please provide either a title or content to analyze'}), 400
        
        # Use the existing analyze_post_content function
        analysis = analyze_post_content(title, content)
        
        if analysis is None:
            return jsonify({'error': 'Analysis failed. Please try again.'}), 500
        
        # Determine if content is malicious
        is_malicious = 'MALICIOUS' in analysis.upper()
        
        return jsonify({
            'analysis': analysis,
            'is_malicious': is_malicious,
            'confidence': 'High' if 'MALICIOUS' in analysis.upper() or 'SAFE' in analysis.upper() else 'Medium',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
