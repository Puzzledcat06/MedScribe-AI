"""
Privacy Masking Module — removes PII before sending to LLM
"""
import re


# Patterns to mask
_PATTERNS = [
    # 10-digit phone numbers (various formats)
    (r'\b(\+91[\-\s]?)?\d{10}\b', '[PHONE]'),
    # Email addresses
    (r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
    # SSN / Aadhaar-style (12-digit) numbers
    (r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b', '[ID]'),
    # Date of birth patterns like DD/MM/YYYY or MM-DD-YYYY
    (r'\b(0?[1-9]|[12][0-9]|3[01])[\/\-\.](0?[1-9]|1[0-2])[\/\-\.](19|20)\d{2}\b', '[DOB]'),
    # Patient file / medical record numbers (MRN-12345)
    (r'\b(MRN|PRN|ID)[\s:\-]?\d+\b', '[MEDICAL_ID]'),
    # Street addresses (simplified)
    (r'\d+\s+[A-Za-z\s]+(Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Nagar|Colony)\b', '[ADDRESS]'),
]


def mask_sensitive_data(text: str) -> str:
    """
    Replace personally identifiable information in the transcript with safe tokens.

    Args:
        text: Raw transcribed text.

    Returns:
        Text with PII replaced by placeholder tokens.
    """
    masked = text
    for pattern, replacement in _PATTERNS:
        masked = re.sub(pattern, replacement, masked, flags=re.IGNORECASE)
    return masked


def get_masked_fields(original: str, masked: str) -> dict:
    """Return a summary of what was masked."""
    tokens = ['[PHONE]', '[EMAIL]', '[ID]', '[DOB]', '[MEDICAL_ID]', '[ADDRESS]']
    return {
        token: masked.count(token)
        for token in tokens
        if masked.count(token) > 0
    }


if __name__ == "__main__":
    sample = (
        "Patient John Doe, phone 9876543210, email john@example.com, "
        "DOB 15/06/1990, Aadhaar 1234 5678 9012, lives at 45 MG Road."
    )
    result = mask_sensitive_data(sample)
    print("Original:", sample)
    print("Masked  :", result)
