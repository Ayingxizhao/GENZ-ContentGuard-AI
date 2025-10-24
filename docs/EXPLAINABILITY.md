# Explainability Feature Documentation

## Overview

The explainability feature provides detailed insights into **why** content was flagged as malicious by highlighting specific toxic phrases with their positions, categories, and severity levels.

## Features

- **Phrase-level Detection**: Identifies specific toxic phrases in analyzed text
- **Position Tracking**: Provides exact character positions (start/end) for each toxic phrase
- **Category Classification**: Categorizes toxic content into 7 distinct types
- **Severity Levels**: Assigns HIGH/MEDIUM/LOW severity to each detected phrase
- **Dual Implementation**: 
  - **Gemini Model**: AI-powered detection via prompt engineering
  - **HuggingFace Model**: Regex-based pattern matching

---

## Toxic Content Categories

| Category | Severity | Description |
|----------|----------|-------------|
| `suicide_self_harm` | HIGH | Suicide encouragement or self-harm language |
| `hate_speech` | HIGH | Hate speech or discriminatory language |
| `threats` | HIGH | Threats or violent language |
| `harassment` | MEDIUM | Harassment or bullying language |
| `body_shaming` | MEDIUM | Body shaming or appearance-based attacks |
| `sexual_content` | MEDIUM | Inappropriate sexual content or harassment |
| `general_toxicity` | LOW | Toxic or aggressive language |

---

## API Usage

### Enable Explainability (Default: Enabled)

Explainability is **enabled by default** for all analysis requests. The API response will include an `explainability` object with detailed information about detected toxic phrases.

### Request Format

```bash
curl -X POST https://plankton-app-xj6ib.ondigitalocean.app/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Post Title",
    "content": "Text to analyze",
    "model": "gemini"
  }'
```

### Response Format

```json
{
  "analysis": "MALICIOUS",
  "confidence": "87.8%",
  "is_malicious": true,
  "risk_level": "HIGH",
  "model_type": "Gemini 2.5 Flash (Finetuned)",
  "explainability": {
    "highlighted_phrases": [
      {
        "text": "kys",
        "start_pos": 45,
        "end_pos": 48,
        "category": "suicide_self_harm",
        "severity": "HIGH",
        "explanation": "Contains suicide encouragement or self-harm language"
      },
      {
        "text": "you're worthless",
        "start_pos": 60,
        "end_pos": 76,
        "category": "harassment",
        "severity": "MEDIUM",
        "explanation": "Contains harassment or bullying language"
      }
    ],
    "categories_detected": {
      "suicide_self_harm": 1,
      "harassment": 1
    },
    "severity_breakdown": {
      "HIGH": 1,
      "MEDIUM": 1,
      "LOW": 0
    },
    "total_matches": 2
  }
}
```

---

## Response Fields

### Explainability Object

| Field | Type | Description |
|-------|------|-------------|
| `highlighted_phrases` | Array | List of detected toxic phrases with details |
| `categories_detected` | Object | Count of phrases per category |
| `severity_breakdown` | Object | Count of phrases per severity level |
| `total_matches` | Integer | Total number of toxic phrases detected |

### Highlighted Phrase Object

| Field | Type | Description |
|-------|------|-------------|
| `text` | String | The exact toxic phrase found in the text |
| `start_pos` | Integer | Character position where phrase starts (0-indexed) |
| `end_pos` | Integer | Character position where phrase ends |
| `category` | String | Toxic content category (see table above) |
| `severity` | String | Severity level: HIGH, MEDIUM, or LOW |
| `explanation` | String | Human-readable explanation of why phrase is toxic |

---

## Frontend Integration

### Displaying Highlighted Text

Use the position data to highlight toxic phrases in your UI:

```javascript
function highlightToxicPhrases(text, phrases) {
  let html = '';
  let lastIndex = 0;
  
  // Sort phrases by position
  const sortedPhrases = phrases.sort((a, b) => a.start_pos - b.start_pos);
  
  sortedPhrases.forEach(phrase => {
    // Add text before highlight
    html += escapeHtml(text.substring(lastIndex, phrase.start_pos));
    
    // Add highlighted phrase
    const severityClass = `severity-${phrase.severity.toLowerCase()}`;
    html += `<span class="${severityClass}" 
                   title="${phrase.explanation}">
              ${escapeHtml(phrase.text)}
            </span>`;
    
    lastIndex = phrase.end_pos;
  });
  
  // Add remaining text
  html += escapeHtml(text.substring(lastIndex));
  
  return html;
}
```

### CSS Styling

```css
/* Severity-based highlighting */
.severity-high {
  background-color: #fee;
  border-bottom: 2px solid #f00;
  cursor: help;
}

.severity-medium {
  background-color: #ffe;
  border-bottom: 2px solid #fa0;
  cursor: help;
}

.severity-low {
  background-color: #fef;
  border-bottom: 2px solid #f0f;
  cursor: help;
}
```

---

## Model Differences

### Gemini 2.5 Flash (AI-Powered)

- **Method**: Prompt engineering with AI analysis
- **Accuracy**: Higher accuracy with context awareness
- **Coverage**: Can detect nuanced toxic content
- **Performance**: Slower (API call to Google)
- **Cost**: Rate-limited (10 requests/day per user)

**Best for**: Critical content moderation requiring highest accuracy

### ContentGuard Model (Regex-Based)

- **Method**: Pattern matching with predefined toxic keywords
- **Accuracy**: Good for explicit toxic language
- **Coverage**: Limited to known patterns
- **Performance**: Fast (local processing)
- **Cost**: Free, unlimited for registered users

**Best for**: High-volume content screening

---

## Example Use Cases

### 1. Content Moderation Dashboard

Display flagged content with inline highlights showing exactly what triggered the flag:

```
User comment: "You should just kys, you're worthless"
                              ^^^              ^^^^^^^^^
                              HIGH             MEDIUM
```

### 2. User Feedback

Help users understand why their content was flagged:

> **Your post was flagged for the following reasons:**
> - "kys" (Suicide & Self-Harm - HIGH severity)
> - "you're worthless" (Harassment - MEDIUM severity)

### 3. Analytics

Track which types of toxic content are most common:

```json
{
  "harassment": 45,
  "hate_speech": 23,
  "sexual_content": 12,
  "general_toxicity": 8
}
```

---

## Technical Implementation

### Pattern Matching (HuggingFace Model)

The regex-based explainability uses compiled patterns from `services/toxic_patterns.py`:

- **Word boundary matching**: Ensures whole-word matches
- **Case-insensitive**: Detects variations in capitalization
- **Overlap handling**: Removes overlapping matches
- **Performance**: Patterns are compiled once and reused

### AI Analysis (Gemini Model)

The Gemini model uses an enhanced prompt that instructs it to:

1. Identify all toxic phrases in the text
2. Determine exact character positions
3. Classify each phrase by category and severity
4. Provide explanations for each detection

---

## Limitations

1. **Context Sensitivity**: Regex patterns may miss context-dependent toxicity
2. **False Positives**: Some phrases may be flagged in non-toxic contexts
3. **Language Support**: Currently optimized for English and Gen Z slang
4. **Pattern Coverage**: Regex-based detection limited to predefined patterns

---

## Future Enhancements

- [ ] Multi-language support
- [ ] User feedback loop for false positives
- [ ] Confidence scores per phrase
- [ ] Contextual analysis improvements
- [ ] Custom pattern definitions per organization
- [ ] Real-time highlighting in text editors

---

## Support

For questions or issues with the explainability feature:

1. Check this documentation
2. Review the [API Reference](../README.md#api-reference)
3. [Open an issue](https://github.com/Ayingxizhao/GENZ-ContentGuard-AI/issues) on GitHub

---

**Built with ❤️ for safer online communities**
