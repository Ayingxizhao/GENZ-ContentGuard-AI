# Gemini Content Classification Testing - Safety Settings Fix

## What It Does

Fixes the Gemini API safety blocking issue in `testingdatasets_gemini.py` to allow content moderation testing and classification of social media posts.

## The Problem

The original script was being blocked by Gemini's safety filters because:
1. The classification prompt contained harmful content examples (for educational purposes)
2. The response output token limit was too low (50 tokens), causing incomplete responses
3. No safety settings were configured to allow content moderation use cases

## How It Works

### Safety Settings Configuration

The fix implements Gemini's official safety settings API with `BLOCK_NONE` thresholds for all harm categories:

```python
SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]
```

These settings are passed to `model.generate_content()` to allow analysis of potentially harmful content for research and moderation purposes.

### Token Limit Increase

Increased `max_output_tokens` from 50 to 5000 to ensure complete classification responses:

```python
generation_config={
    "temperature": 0.1,
    "max_output_tokens": 5000
}
```

### Model Configuration

Creates a plain-text Gemini model instance (not JSON mode) to allow flexible text classification responses:

```python
model = genai.GenerativeModel('gemini-2.5-flash')
```

## How to Use

### Run the testing script:

```bash
cd preprocessing
python testingdatasets_gemini.py
```

### Configure test data:

Edit line 130 in `testingdatasets_gemini.py` to adjust the number of rows to test:

```python
df = pd.read_csv(data_path, nrows=5)  # Change nrows as needed
```

### Expected output:

```
🧪 TESTING PROMPT ON DATASET
============================================================
✅ Test complete!
Total examples: 5
Successful: 5
Errors: 0
Results saved to: preprocessing/gemini_test_results_TIMESTAMP.csv
```

### Results format:

CSV file with columns:
- `content`: Original social media post
- `classification`: Classification result (e.g., "Classification: OK\nConfidence: 5")
- `status`: Processing status ("success" or error message)

## Important Notes

### Legitimate Use Case

These safety settings with `BLOCK_NONE` should **only be used for**:
- Content moderation research
- Training and testing classification systems
- Academic analysis of harmful content

### Not for Production

For production content analysis, use more restrictive safety thresholds or implement additional safeguards.

### API Key Required

Ensure `GEMINI_API_KEY` is set in your `.env` file or the script will prompt for it.

## Files Modified

- `preprocessing/testingdatasets_gemini.py` - Added safety settings and increased token limits
- `preprocessing/docs/gemini_testing_fix.md` - This documentation

## Technical Details

- **Model**: gemini-2.5-flash
- **Temperature**: 0.1 (for consistent classification)
- **Max Output Tokens**: 5000
- **Safety Threshold**: BLOCK_NONE (all categories)
- **Response Mode**: Plain text (not JSON)
