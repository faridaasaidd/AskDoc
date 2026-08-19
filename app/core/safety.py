import re
from typing import Tuple

# Maximum allowed characters for input question
MAX_INPUT_LENGTH = 2000

# Regex blocklist patterns for fast input prompt injection detection
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous\s+)?instructions",
    r"system\s+prompt\s+override",
    r"you\s+are\s+now\s+dan",
    r"do\s+anything\s+now",
    r"jailbreak",
    r"forget\s+(all\s+)?(previous|prior)\s+rules",
    r"bypass\s+safety\s+filter",
]

# Regex patterns for outgoing PII detection & redaction
PII_PATTERNS = {
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "PHONE": r"\b(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
}


def sanitize_and_validate_input(text: str) -> Tuple[bool, str]:
    """
    Input Guardrail: Validates user input before reaching the LLM.
    Checks input length limits and prompt injection blocklist patterns.
    """
    if not text or not text.strip():
        return False, "Input question cannot be empty."

    if len(text) > MAX_INPUT_LENGTH:
        return False, f"Question exceeds maximum allowed length of {MAX_INPUT_LENGTH} characters."

    lower_text = text.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, lower_text):
            return False, "Potential prompt injection attempt detected."

    return True, ""


def redact_pii(text: str) -> str:
    """
    Output Guardrail: Scans outgoing text for PII (Emails, Phone numbers, SSNs, Credit Cards)
    and replaces matches with [REDACTED_<TYPE>].
    """
    if not text:
        return text

    redacted = text
    for pii_type, pattern in PII_PATTERNS.items():
        redacted = re.sub(pattern, f"[REDACTED_{pii_type}]", redacted)

    return redacted
