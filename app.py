"""Main application entry point."""

from app import create_app

# Create Flask application instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5001)