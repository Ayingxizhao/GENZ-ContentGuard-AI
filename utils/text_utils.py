"""
Text processing utilities for token management and smart truncation.
"""
import re
import logging

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not available, using character-based estimation")


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in text.
    
    Uses tiktoken if available, otherwise falls back to character-based estimation.
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    if not text:
        return 0
    
    if TIKTOKEN_AVAILABLE:
        try:
            # Use cl100k_base encoding (GPT-4, similar to Gemini)
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception as e:
            logging.warning(f"tiktoken encoding failed: {e}, falling back to estimation")
    
    # Fallback: 1 token ≈ 4 characters
    return len(text) // 4


def find_sentence_boundary(text: str, target_pos: int, direction: str = 'backward') -> int:
    """
    Find the nearest sentence boundary from target position.
    
    Args:
        text: Input text
        target_pos: Target character position
        direction: 'backward' or 'forward'
        
    Returns:
        Position of sentence boundary
    """
    if not text or target_pos <= 0:
        return 0
    if target_pos >= len(text):
        return len(text)
    
    # Sentence ending patterns
    sentence_ends = r'[.!?]\s+'
    
    if direction == 'backward':
        # Search backward for sentence end
        search_text = text[:target_pos]
        matches = list(re.finditer(sentence_ends, search_text))
        if matches:
            # Return position after the sentence ending
            return matches[-1].end()
        return 0
    else:
        # Search forward for sentence end
        search_text = text[target_pos:]
        match = re.search(sentence_ends, search_text)
        if match:
            return target_pos + match.end()
        return len(text)


def smart_truncate(text: str, max_tokens: int, preserve_sentences: bool = True) -> tuple[str, bool]:
    """
    Intelligently truncate text to fit within token limit.
    
    Args:
        text: Input text to truncate
        max_tokens: Maximum number of tokens allowed
        preserve_sentences: If True, truncate at sentence boundaries
        
    Returns:
        Tuple of (truncated_text, was_truncated)
    """
    if not text:
        return "", False
    
    current_tokens = estimate_tokens(text)
    
    # No truncation needed
    if current_tokens <= max_tokens:
        return text, False
    
    # Calculate target character position (rough estimate)
    ratio = max_tokens / current_tokens
    target_chars = int(len(text) * ratio * 0.95)  # 95% to be safe
    
    if preserve_sentences:
        # Find nearest sentence boundary
        truncate_pos = find_sentence_boundary(text, target_chars, 'backward')
        
        # If no sentence boundary found, fall back to character truncation
        if truncate_pos == 0:
            truncate_pos = target_chars
    else:
        truncate_pos = target_chars
    
    truncated = text[:truncate_pos].strip()
    
    # Verify token count and adjust if needed
    while estimate_tokens(truncated) > max_tokens and len(truncated) > 100:
        # Reduce by 10% and try again
        truncate_pos = int(truncate_pos * 0.9)
        if preserve_sentences:
            truncate_pos = find_sentence_boundary(text, truncate_pos, 'backward')
        truncated = text[:truncate_pos].strip()
    
    return truncated, True


def progressive_truncate(text: str, max_tokens: int, attempt: int = 0) -> tuple[str, float]:
    """
    Progressively reduce text size based on attempt number.
    
    Args:
        text: Input text
        max_tokens: Maximum tokens allowed
        attempt: Attempt number (0 = full, 1 = 75%, 2 = 50%, 3 = 25%)
        
    Returns:
        Tuple of (truncated_text, reduction_percentage)
    """
    reduction_levels = [1.0, 0.75, 0.5, 0.25]
    
    if attempt >= len(reduction_levels):
        attempt = len(reduction_levels) - 1
    
    reduction = reduction_levels[attempt]
    target_tokens = int(max_tokens * reduction)
    
    truncated, was_truncated = smart_truncate(text, target_tokens, preserve_sentences=True)
    
    return truncated, reduction


def adjust_phrase_positions(phrases: list, original_text: str, truncated_text: str) -> list:
    """
    Adjust highlighted phrase positions after text truncation.
    
    Args:
        phrases: List of phrase dicts with 'text', 'start_pos', 'end_pos'
        original_text: Original full text
        truncated_text: Truncated text
        
    Returns:
        List of phrases that are still within truncated text
    """
    if not phrases or not truncated_text:
        return []
    
    truncated_length = len(truncated_text)
    adjusted_phrases = []
    
    for phrase in phrases:
        start_pos = phrase.get('start_pos', 0)
        end_pos = phrase.get('end_pos', 0)
        
        # Skip phrases that are beyond truncation point
        if start_pos >= truncated_length:
            continue
        
        # Adjust end position if it extends beyond truncation
        if end_pos > truncated_length:
            end_pos = truncated_length
        
        # Verify the phrase text still matches
        phrase_text = phrase.get('text', '')
        if start_pos >= 0 and end_pos <= truncated_length:
            actual_text = truncated_text[start_pos:end_pos]
            if actual_text == phrase_text or phrase_text in actual_text:
                adjusted_phrases.append(phrase)
    
    return adjusted_phrases


def get_truncation_summary(original_length: int, truncated_length: int, 
                          original_tokens: int, truncated_tokens: int) -> str:
    """
    Generate a human-readable truncation summary.
    
    Args:
        original_length: Original character count
        truncated_length: Truncated character count
        original_tokens: Original token count
        truncated_tokens: Truncated token count
        
    Returns:
        Summary string
    """
    char_reduction = ((original_length - truncated_length) / original_length * 100)
    token_reduction = ((original_tokens - truncated_tokens) / original_tokens * 100)
    
    return (f"Truncated from {original_length} chars ({original_tokens} tokens) "
            f"to {truncated_length} chars ({truncated_tokens} tokens). "
            f"Reduced by {char_reduction:.1f}% chars, {token_reduction:.1f}% tokens.")
