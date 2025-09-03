# 🛡️ GENZ ContentGuard AI

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--learn-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

> **AI-powered malicious content detection system optimized for Gen Z language patterns**

GENZ ContentGuard AI is an advanced machine learning system designed to detect and analyze malicious content, hate speech, harassment, and harmful language patterns commonly used in modern online communication, with special focus on Gen Z language and internet slang.

## 🌟 Features

### 🔍 **Advanced Content Analysis**
- **Real-time Detection**: Instant analysis of text content for malicious patterns
- **Multi-Category Classification**: Detects 11+ types of harmful content:
  - Suicide/Self-harm content
  - Hate speech and discrimination
  - Violence and threats
  - Bullying and harassment
  - Body shaming and appearance-based attacks
  - Mental health shaming
  - Gen Z slang harassment patterns
  - Online harassment tactics
  - Sexual harassment and exploitation
  - Scams and fraud attempts
  - Conspiracy theories and misinformation
  - Trolling and baiting behavior

### 📊 **Detailed Analysis Reports**
- **Risk Assessment**: HIGH/MEDIUM/LOW risk levels with explanations
- **Keyword Detection**: Specific harmful and positive keywords identified
- **Context Analysis**: Understanding of language context and intent
- **Confidence Scoring**: Probability-based confidence levels
- **Comprehensive Explanations**: Detailed breakdown of findings and recommendations

### 🎯 **Gen Z Language Optimization**
- **Modern Slang Detection**: Recognizes contemporary internet language
- **Emoji and Symbol Handling**: Processes modern communication patterns
- **Context-Aware Analysis**: Understands nuanced language usage
- **Cultural Sensitivity**: Adapts to evolving language trends

### 🖥️ **Modern Web Interface**
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Real-time Analysis**: Instant feedback and results
- **Visual Indicators**: Color-coded risk levels and categories
- **User-Friendly**: Clean, intuitive interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/contentguard-ai.git
   cd contentguard-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the model** (if using custom data)
   ```bash
   python data_processor.py
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the web interface**
   Open your browser and navigate to `http://localhost:5001`

## 📁 Project Structure

```
contentguard-ai/
├── app.py                 # Main Flask application
├── data_processor.py      # Data processing and model training
├── local_model.py         # Local ML model implementation
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface template
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── script.js     # Frontend functionality
├── genz_detector_model.pkl # Trained ML model
└── README.md             # This file
```

## 🔧 Technical Details

### **API Endpoints**
- `POST /analyze` - Analyze text content
- `GET /model-info` - Get model information
- `GET /health` - Health check endpoint

## 📊 Example Usage

### API Request
```bash
curl -X POST http://localhost:5001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Post",
    "content": "This is a test message for analysis."
  }'
```

### API Response
```json
{
  "analysis": "SAFE",
  "confidence": "85.2%",
  "is_malicious": false,
  "detailed_analysis": {
    "risk_level": "LOW",
    "elements_scanned": 2,
    "explanation": "✅ Detected Positive Elements: Positive Support, Health Wellness...",
    "keyword_analysis": {
      "malicious_keywords": {},
      "safe_keywords": {
        "positive_support": ["help", "support"],
        "health_wellness": ["health"]
      }
    }
  }
}
```

## 🎯 Use Cases

- **Social Media Moderation**: Automated content filtering
- **Online Communities**: Community safety and moderation
- **Educational Platforms**: Safe learning environments
- **Gaming Communities**: Toxicity detection and prevention
- **Customer Support**: Automated harmful content detection

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Reddit community for providing training data
- Scikit-learn team for the excellent ML framework
- Flask community for the web framework
- All contributors and users of this project

---

<div align="center">
  <p>Made with ❤️ for a safer internet</p>
  <p><strong>ContentGuard AI</strong> - Protecting digital spaces one message at a time</p>
</div>
