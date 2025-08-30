# GenZ Malicious Content Detector - Chrome Extension

A Chrome extension that uses machine learning to detect malicious GenZ language and content while browsing social media platforms.

## Features

- 🔍 **Real-time Content Analysis**: Automatically scans social media content for malicious language
- 🎯 **GenZ-Specific Detection**: Trained on modern online harassment patterns and GenZ slang
- ⚡ **Fast Local Model**: Uses a lightweight ML model for quick analysis
- 🤖 **OpenAI Fallback**: Optional GPT-4 analysis for higher accuracy
- 🎨 **Visual Indicators**: Clear warnings and visual cues for malicious content
- ⚙️ **Customizable Settings**: Adjust sensitivity and scanning preferences

## Installation

### Prerequisites
1. Make sure your Flask API server is running on `http://localhost:5001`
2. Ensure the trained model file `genz_detector_model.pkl` exists in your project root

### Install Extension
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `extension` folder from this project
5. The extension should now appear in your extensions list

## Usage

### Manual Analysis
1. Click the extension icon in your browser toolbar
2. Paste or type text in the input area
3. Click "Analyze" or press Ctrl+Enter
4. View the analysis result with confidence score

### Automatic Scanning
1. Enable "Auto-scan" in the extension settings
2. Browse social media platforms (Reddit, Twitter, etc.)
3. Malicious content will be automatically highlighted with red borders
4. Click the warning icon (⚠️) for detailed analysis

### Context Menu
1. Select any text on a webpage
2. Right-click and choose "Analyze with GenZ Detector"
3. View the analysis result

## Supported Platforms

- Reddit
- Twitter/X
- Facebook
- Instagram
- TikTok
- YouTube
- And other social media platforms

## Settings

- **Sensitivity**: Adjust detection threshold (0-100%)
- **Auto-scan**: Enable automatic content scanning
- **Use OpenAI**: Switch to GPT-4 for higher accuracy (slower, requires API key)

## Technical Details

### Model Performance
- **Accuracy**: 88.9% on test cases
- **Speed**: ~0.002 seconds per prediction
- **Model Type**: Multinomial Naive Bayes with TF-IDF features

### Detected Content Types
- Suicide encouragement ("kys", "unalive yourself")
- Hate speech and discrimination
- Online harassment and bullying
- Violent threats
- GenZ-specific malicious language
- Body shaming and appearance-based attacks

## Development

### Project Structure
```
extension/
├── manifest.json          # Extension configuration
├── popup/                 # Popup interface
│   ├── popup.html
│   ├── popup.css
│   └── popup.js
├── content/               # Content scripts
│   ├── content.js
│   └── content.css
├── background/            # Background script
│   └── background.js
└── icons/                 # Extension icons
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

### API Endpoints
- `POST /analyze` - Analyze text content
- `GET /model-info` - Get model status
- `GET /health` - Health check

## Troubleshooting

### Extension Not Working
1. Check that your Flask server is running on port 5001
2. Verify the model file exists: `genz_detector_model.pkl`
3. Check browser console for error messages
4. Ensure the extension has proper permissions

### Model Not Loading
1. Run `python data_processor.py` to generate the model
2. Check that the model file is in the correct location
3. Restart the Flask server

### Performance Issues
1. Disable auto-scan for better performance
2. Use local model instead of OpenAI
3. Reduce sensitivity setting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the browser console for errors
3. Ensure all prerequisites are met
4. Create an issue in the repository
