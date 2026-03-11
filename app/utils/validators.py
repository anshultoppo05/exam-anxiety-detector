"""Input validation utilities."""

import re


def validate_text_input(text):
    """Validate and sanitize text input. Returns cleaned text or raises ValueError."""
    if not text or not isinstance(text, str):
        raise ValueError("Text input is required and must be a non-empty string.")

    # Strip HTML tags
    cleaned = re.sub(r"<[^>]+>", "", text)
    cleaned = cleaned.strip()

    if not cleaned:
        raise ValueError("Text input must not be empty after sanitization.")

    if len(cleaned) > 10000:
        raise ValueError("Text input must not exceed 10,000 characters.")

    # Reject suspicious prompt-injection patterns
    injection_patterns = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"forget\s+(all\s+)?previous",
        r"you\s+are\s+now\s+a",
        r"system\s*:\s*",
        r"<\|im_start\|>",
    ]
    for pattern in injection_patterns:
        if re.search(pattern, cleaned, re.IGNORECASE):
            raise ValueError("Input contains disallowed patterns.")

    return cleaned
