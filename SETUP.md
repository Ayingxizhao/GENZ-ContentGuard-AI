# ContentGuard AI - Setup Guide

## Overview
ContentGuard AI is a web application that uses AI to detect malicious content, hate speech, harassment, and threats in text. It's specifically designed to handle Gen Z language patterns and internet slang.

## Prerequisites
- Python 3.8 or higher
- OpenAI API key
- pip (Python package manager)

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root with the following content:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key_here
   SECRET_KEY=your_secret_key_here
   FLASK_DEBUG=True
   ```
   
   **Tip:** You can copy from `env.example` and rename it to `.env`
   
   **Important**: Replace `your_actual_openai_api_key_here` with your real OpenAI API key.

4. **Get an OpenAI API key**
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Sign up or log in
   - Navigate to API Keys section
   - Create a new API key
   - Copy the key and paste it in your `.env` file

## Running the Application

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Open your web browser**
   Navigate to: `http://localhost:5001`

3. **Use the application**
   - Enter text in the content field
   - Optionally add a title
   - Click "Analyze Content" or press Ctrl+Enter
   - View the AI analysis results

## Features

- **Real-time Analysis**: Get instant feedback on text content
- **Modern UI**: Clean, responsive design that works on all devices
- **AI-Powered**: Uses OpenAI's GPT models for accurate detection
- **Contextual Understanding**: Handles Gen Z slang and internet language
- **Multiple Input Types**: Supports both titles and content
- **Detailed Results**: Shows analysis, confidence level, and timestamp

## API Endpoints

- `GET /` - Main web interface
- `POST /analyze` - Analyze text content
- `GET /health` - Health check endpoint

## Configuration Options

You can modify the following in `config.py`:
- Maximum content length
- Debug mode
- Secret key
- API configurations

## Troubleshooting

1. **"OPENAI_API_KEY environment variable is required"**
   - Make sure you have a `.env` file
   - Check that your API key is correct
   - Restart the application after making changes

2. **"Analysis failed"**
   - Check your internet connection
   - Verify your OpenAI API key is valid
   - Check your OpenAI account has sufficient credits

3. **Port already in use**
   - Change the port in `app.py` (line 78)
   - Or kill the process using the port

## Security Notes

- Never commit your `.env` file to version control
- Keep your OpenAI API key secure
- The application is designed for development use by default
- For production deployment, set `FLASK_DEBUG=False`

## Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your API key and configuration
3. Check the OpenAI API status page
4. Review the Flask application logs

## License

This project is for research and educational purposes.
