"""Main application routes."""

import time
from typing import Tuple, Union

from flask import Blueprint, Response, jsonify, render_template, request

from local_model import analyze_with_local_model, local_detector

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index() -> str:
    """Main page route."""
    return render_template("index.html")


@main_bp.route("/analyze", methods=["POST"])
def analyze() -> Union[Response, Tuple[Response, int]]:
    """Analyze content for malicious language using local model only."""
    try:
        data = request.get_json()
        title = data.get("title", "")
        content = data.get("content", "")

        if not title and not content:
            return jsonify({"error": "Please provide either a title or content to analyze"}), 400

        # Use local model only
        if local_detector.model_loaded:
            result = analyze_with_local_model(title, content)
            model_source = "local"
        else:
            return jsonify({"error": "No models loaded. Please train models first."}), 500

        if "error" not in result:
            response_data = {
                "analysis": result["analysis"],
                "is_malicious": result["is_malicious"],
                "confidence": result["confidence"],
                "model_type": result["model_type"],
                "probabilities": result["probabilities"],
                "model_source": model_source,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Add detailed analysis if available
            if "detailed_analysis" in result:
                response_data["detailed_analysis"] = result["detailed_analysis"]

            return jsonify(response_data)
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@main_bp.route("/model-info")
def model_info() -> Union[Response, Tuple[Response, int]]:
    """Get information about available models (local only)."""
    return jsonify(
        {
            "local_model": local_detector.get_model_info(),
            "openai_available": False,
        }
    )


@main_bp.route("/health")
def health() -> Union[Response, Tuple[Response, int]]:
    """Health check endpoint."""
    return jsonify({"status": "healthy"})
