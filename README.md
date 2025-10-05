# 🛡️ ContentGuard AI

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

> **AI-powered content moderation for modern teenage communities**

ContentGuard AI detects malicious language, hate speech, harassment, and threats in real-time. Built specifically for Gen Z communication patterns, it understands modern slang, internet language, and evolving online behaviors.

---

## 🚀 Getting Started

### Web Interface [https://plankton-app-xj6ib.ondigitalocean.app/](https://plankton-app-xj6ib.ondigitalocean.app/)
Visit our platform to analyze content instantly:
1. Navigate to the homepage
2. Enter text in the analysis form (title + content)
3. Click **"Analyze Content"** 
4. View detailed results with risk assessment and recommendations

### API Integration
Integrate ContentGuard into your platform via REST API:

**Endpoint:** `POST /analyze`

**Request:**
```json
{
  "title": "Post Title",
  "content": "Text content to analyze"
}
```

**Response:**
```json
{
  "analysis": "SAFE",
  "confidence": "92.5%",
  "is_malicious": false,
  "risk_level": "LOW",
  "explanation": "Content appears safe with positive language patterns detected.",
  "keyword_analysis": {
    "malicious_keywords": [],
    "safe_keywords": ["support", "help", "community"]
  }
}
```

---

## ✨ Features

### 🔍 Real-Time Content Analysis
- **Instant Detection**: Analyze text in milliseconds
- **Multi-Category Classification**: Identifies 11+ types of harmful content including suicide/self-harm, hate speech, harassment, threats, body shaming, and scams
- **Confidence Scoring**: Probability-based risk assessment (HIGH/MEDIUM/LOW)

### 🎯 Gen Z Language Understanding
- **Modern Slang Recognition**: Trained on contemporary internet language
- **Context-Aware**: Distinguishes between harmful intent and casual usage
- **Emoji & Symbol Processing**: Handles modern communication patterns
- **Evolving Detection**: Adapts to new language trends

### 📊 Detailed Reporting
- **Risk Level Assessment**: Clear HIGH/MEDIUM/LOW classification
- **Keyword Breakdown**: Specific harmful and safe keywords identified
- **Actionable Recommendations**: Guidance for content moderation decisions
- **Visual Indicators**: Color-coded results for quick scanning

### 🔐 Authentication & Rate Limiting
- **OAuth Integration**: Sign in with Google or GitHub
- **Usage Tracking**: Monitor API calls per day
- **Rate Limits**: Fair usage policies for all users

---

## 🎯 Use Cases

- **Social Media Platforms**: Automated content moderation at scale
- **Online Communities**: Protect members from harassment and hate speech
- **Educational Platforms**: Maintain safe learning environments
- **Gaming Communities**: Detect and prevent toxic behavior
- **Customer Support**: Flag harmful messages for review

---

## 📖 How It Works

1. **Submit Content**: Provide text via web interface or API
2. **AI Analysis**: Our ML model processes language patterns, context, and keywords
3. **Risk Assessment**: Content is classified as SAFE or MALICIOUS with confidence score
4. **Detailed Report**: Receive breakdown of findings with specific keywords and recommendations
5. **Take Action**: Use insights to moderate, flag, or approve content

---

## 🛠️ API Reference

### Authentication
Sign in via OAuth (Google/GitHub) to access API features and track usage.

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | Analyze text content |
| `GET` | `/auth/user` | Get current user info |
| `GET` | `/health` | Service health check |

### Rate Limits
- **Free Tier**: 100 requests/day
- **Authenticated Users**: Higher limits based on account type

---

## 🐛 Report Issues

Found a bug or have a feature request? Visit our [Bug Report Page](/bug-report) or [open an issue](https://github.com/Ayingxizhao/GENZ-ContentGuard-AI/issues).

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
