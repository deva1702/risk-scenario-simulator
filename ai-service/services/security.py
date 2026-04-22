import re

# Maximum allowed input length
MAX_INPUT_LENGTH = 1000

# Simple patterns to detect prompt injection attempts
PROMPT_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"disregard\s+all\s+instructions",
    r"reveal\s+(system|hidden|secret)",
    r"you\s+are\s+now",
]

# Pattern to remove HTML tags
HTML_PATTERN = re.compile(r"<[^>]+>")  # safer than <.*?>


def detect_prompt_injection(text: str) -> bool:
    """
    Detect common prompt injection patterns.
    Uses lowercase normalization for simplicity.
    """
    text = text.lower()
    return any(re.search(pattern, text) for pattern in PROMPT_PATTERNS)


def sanitize(text: str) -> str:
    """
    Remove HTML tags and trim whitespace.
    """
    return re.sub(HTML_PATTERN, "", text).strip()


def validate_input(text: str):
    """
    Validate user input before processing.
    Returns:
        (True, None) if valid
        (False, error_message) if invalid
    """

    if not isinstance(text, str):
        return False, "Input must be a string"

    if not text.strip():
        return False, "Input cannot be empty"

    if len(text) > MAX_INPUT_LENGTH:
        return False, "Input too long (max 1000 chars)"

    if detect_prompt_injection(text):
        return False, "Prompt injection detected"

    return True, None