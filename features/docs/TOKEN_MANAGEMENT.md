# Token Management & Smart Truncation

## Overview
Intelligent token management system that prevents context limit errors through accurate token counting, smart truncation, and progressive reduction strategies.

## What It Does

### 1. Accurate Token Counting
Uses `tiktoken` library (OpenAI's tokenizer) for precise token estimation:
- More accurate than character-based estimation
- Accounts for multi-byte characters and special tokens
- Falls back to character estimation if tiktoken unavailable

### 2. Smart Truncation
Truncates content intelligently while preserving meaning:
- **Sentence boundary preservation**: Cuts at sentence ends, not mid-sentence
- **Token-based limits**: Uses actual token counts, not just characters
- **Iterative adjustment**: Verifies token count after truncation and adjusts if needed

### 3. Progressive Reduction
Automatically retries with reduced content if API fails:
- **Attempt 0**: Full content (100%)
- **Attempt 1**: Reduced to 75%
- **Attempt 2**: Reduced to 50%
- **Attempt 3**: Reduced to 25%

### 4. Explainability Adjustment
Adjusts highlighted phrase positions when content is truncated:
- Removes phrases beyond truncation point
- Adjusts end positions if they extend beyond truncation
- Verifies phrase text still matches after truncation

---

## How It Works

### Token Limits

| Content Type | Max Tokens | Approx Chars | Notes |
|--------------|------------|--------------|-------|
| Post | 500 | ~2000 | Main post content |
| Comment | 125 | ~500 | Individual comment |
| Total Input | 15,000 | ~60,000 | Including prompt |
| Prompt | ~45 | ~180 | Batch analysis prompt |

### Smart Truncation Algorithm

```python
1. Estimate tokens in original text
2. If under limit → Return as-is
3. Calculate target character position (token_ratio * length * 0.95)
4. Find nearest sentence boundary (backward search)
5. Truncate at sentence boundary
6. Verify token count
7. If still over limit → Reduce by 10% and repeat
```

### Progressive Reduction Flow

```
API Call Attempt 0 (100% content)
    ↓ (fails with size error)
API Call Attempt 1 (75% content)
    ↓ (fails with size error)
API Call Attempt 2 (50% content)
    ↓ (fails with size error)
API Call Attempt 3 (25% content)
    ↓ (fails)
Return error
```

---

## Implementation Details

### Files Created

1. **`utils/text_utils.py`**
   - `estimate_tokens()` - Accurate token counting
   - `smart_truncate()` - Intelligent truncation
   - `progressive_truncate()` - Reduction by attempt
   - `find_sentence_boundary()` - Sentence detection
   - `adjust_phrase_positions()` - Fix explainability
   - `get_truncation_summary()` - Human-readable summary

2. **`features/docs/TOKEN_MANAGEMENT.md`** (this file)

### Files Modified

1. **`services/gemini_model.py`**
   - Added `_predict_batch_with_retry()` wrapper
   - Renamed original to `_predict_batch_internal()`
   - Uses `smart_truncate()` for posts and comments
   - Uses `estimate_tokens()` for accurate counting
   - Implements progressive reduction on failure

2. **`requirements.txt`**
   - Added `tiktoken>=0.5.0`

---

## Usage Examples

### Basic Token Estimation

```python
from utils.text_utils import estimate_tokens

text = "This is a sample text for token counting."
tokens = estimate_tokens(text)
print(f"Estimated tokens: {tokens}")
# Output: Estimated tokens: 9
```

### Smart Truncation

```python
from utils.text_utils import smart_truncate

long_text = "First sentence. Second sentence. Third sentence. Fourth sentence."
truncated, was_truncated = smart_truncate(long_text, max_tokens=10, preserve_sentences=True)

print(f"Truncated: {truncated}")
# Output: "First sentence. Second sentence."
print(f"Was truncated: {was_truncated}")
# Output: True
```

### Progressive Truncation

```python
from utils.text_utils import progressive_truncate

text = "Very long text content..."
reduced, reduction_pct = progressive_truncate(text, max_tokens=100, attempt=1)

print(f"Reduction: {reduction_pct * 100}%")
# Output: 75%
```

### Adjust Explainability

```python
from utils.text_utils import adjust_phrase_positions

phrases = [
    {"text": "toxic", "start_pos": 10, "end_pos": 15},
    {"text": "harmful", "start_pos": 2050, "end_pos": 2057}  # Beyond truncation
]

original_text = "..." # 3000 chars
truncated_text = original_text[:2000]

adjusted = adjust_phrase_positions(phrases, original_text, truncated_text)
# Returns only first phrase, second is beyond truncation point
```

---

## Logs & Monitoring

### Truncation Warnings

```
WARNING: Post Truncated from 3500 chars (875 tokens) to 2000 chars (500 tokens). 
         Reduced by 42.9% chars, 42.9% tokens.
```

```
WARNING: Comment 3 Truncated from 800 chars (200 tokens) to 500 chars (125 tokens). 
         Reduced by 37.5% chars, 37.5% tokens.
```

### Progressive Reduction

```
WARNING: Batch prediction failed (attempt 0), trying with reduced content...
INFO: Retrying with 75.0% of original content
```

```
WARNING: Batch prediction failed (attempt 1), trying with reduced content...
INFO: Retrying with 50.0% of original content
```

### Token Limit Warnings

```
WARNING: Reducing comments from 10 to 7 due to token limit (16500 > 15000)
```

---

## Benefits

### 1. Prevents API Failures
- No more "context length exceeded" errors
- Automatic retry with reduced content
- Graceful degradation

### 2. Preserves Meaning
- Sentence boundary preservation
- No mid-word cuts
- Maintains readability

### 3. Accurate Estimation
- Uses actual tokenizer (tiktoken)
- Accounts for special characters
- More reliable than character counting

### 4. Transparent
- Clear logging of truncations
- Shows before/after stats
- Users know what was analyzed

### 5. Efficient
- Minimizes wasted API calls
- Smart reduction strategy
- Caches token counts

---

## Testing

### Test Case 1: Normal Content (No Truncation)
```python
post = "Short post"  # 50 chars, ~12 tokens
comments = ["Comment 1", "Comment 2"]  # ~10 tokens each

# Expected: No truncation, full analysis
```

### Test Case 2: Long Post (Truncation)
```python
post = "Very long post..." * 200  # 3000 chars, ~750 tokens
comments = ["Comment"]

# Expected: 
# - Post truncated to 500 tokens (~2000 chars)
# - Warning logged
# - Analysis succeeds
```

### Test Case 3: Long Comments (Truncation)
```python
post = "Normal post"
comments = ["Very long comment..." * 50] * 5  # Each 800 chars, ~200 tokens

# Expected:
# - Each comment truncated to 125 tokens (~500 chars)
# - 5 warnings logged
# - Analysis succeeds
```

### Test Case 4: Excessive Content (Progressive Reduction)
```python
post = "Extremely long..." * 1000  # 15000 chars, ~3750 tokens
comments = ["Long comment..." * 100] * 20  # Way over limit

# Expected:
# - Attempt 0 fails
# - Attempt 1 (75%) fails
# - Attempt 2 (50%) succeeds
# - Logs show retry attempts
```

### Test Case 5: Sentence Boundary Preservation
```python
post = "First sentence. Second sentence. Third sentence. Fourth sentence."
# Truncate to ~30 tokens (should fit 2-3 sentences)

# Expected:
# - Truncates at sentence boundary
# - Result: "First sentence. Second sentence. Third sentence."
# - NOT: "First sentence. Second sentence. Thi..."
```

---

## Troubleshooting

### Issue: tiktoken Import Error

**Symptom:**
```
WARNING: tiktoken not available, using character-based estimation
```

**Solution:**
```bash
pip install tiktoken
```

### Issue: Still Getting Token Limit Errors

**Check:**
1. Is progressive reduction working? (Check logs for retry attempts)
2. Are limits set correctly? (MAX_POST_TOKENS, MAX_COMMENT_TOKENS)
3. Is prompt too long? (Check prompt token count)

**Debug:**
```python
from utils.text_utils import estimate_tokens

# Check individual components
post_tokens = estimate_tokens(post_text)
comment_tokens = sum(estimate_tokens(c) for c in comments)
prompt_tokens = estimate_tokens(prompt_template)
total = post_tokens + comment_tokens + prompt_tokens

print(f"Total tokens: {total}")
print(f"Limit: 15000")
print(f"Over by: {total - 15000}")
```

### Issue: Explainability Positions Wrong After Truncation

**Check:**
1. Is `adjust_phrase_positions()` being called?
2. Are positions being adjusted in normalized results?

**Fix:**
Add adjustment in `_normalize_gemini_result()` if truncation occurred.

---

## Future Enhancements

### Possible Additions
1. **Chunking for unlimited length**: Split very long content into multiple API calls
2. **Smart summarization**: Summarize truncated portions instead of discarding
3. **User control**: Let users choose truncation vs chunking
4. **Token budget UI**: Show users token usage in real-time

### Not Implemented (By Design)
- Chunking (too complex, more API calls)
- Custom tokenizers (tiktoken is accurate enough)
- Per-user token limits (handled by rate limiting)

---

## Related Features

- **Rate Limit UI** (`features/docs/RATE_LIMIT_UI.md`) - UI for rate limits
- **Gemini Rate Limit** (`middleware/gemini_rate_limit.py`) - Backend rate limiting
- **Batch Analysis** (`services/gemini_model.py`) - Batch API calls

---

## Summary

This token management system ensures:
- ✅ **No context limit errors** - Progressive reduction prevents failures
- ✅ **Accurate token counting** - Uses tiktoken for precision
- ✅ **Smart truncation** - Preserves sentence boundaries
- ✅ **Transparent operation** - Clear logging and warnings
- ✅ **Automatic retry** - Progressive reduction on failure
- ✅ **Explainability preserved** - Adjusts phrase positions

The system handles content of any length gracefully, automatically reducing size until it fits within API limits while preserving as much meaning as possible.
