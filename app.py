import time

from flask import Flask, jsonify, render_template, request, Response, Tuple
from typing import Union
from flask_cors import CORS

from local_model import analyze_with_local_model, local_detector

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze() -> Union[Response, Tuple[Response, int]]:
    try:
        data = request.get_json()
        title = data.get("title", "")
        content = data.get("content", "")

        if not title and not content:
            return jsonify({"error": "Please provide either a title or content to analyze"}), 400

        # Use local model for analysis
        if local_detector.model_loaded:
            result = analyze_with_local_model(title, content)

            if "error" not in result:
                response_data = {
                    "analysis": result["analysis"],
                    "is_malicious": result["is_malicious"],
                    "confidence": result["confidence"],
                    "model_type": result["model_type"],
                    "probabilities": result["probabilities"],
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                }

                # Add detailed analysis if available
                if "detailed_analysis" in result:
                    response_data["detailed_analysis"] = result["detailed_analysis"]

                return jsonify(response_data)

        # If local model is not loaded
        return jsonify({"error": "Local model not loaded. Please run data_processor.py first."}), 500

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/model-info")
def model_info() -> Union[Response, Tuple[Response, int]]:
    """Get information about available models"""
    return jsonify({"local_model": local_detector.get_model_info(), "openai_available": False})


@app.route("/health")
def health() -> Union[Response, Tuple[Response, int]]:
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5001)
