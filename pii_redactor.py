"""
PII redaction -- runs BEFORE any ticket text reaches an LLM.

- Regex-based for emails and phone numbers
- Database-driven for customer names (matched against known customers)
- Returns a pii_mapping so PII can be restored in the final customer-facing reply
"""
import re

from data.loader import CUSTOMERS_DB

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
# 10 digits written as 5551234567, 555-123-4567 or 555.123.4567
PHONE_PATTERN = re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")

KNOWN_NAMES = {customer["name"] for customer in CUSTOMERS_DB.values()}
KNOWN_FIRST_NAMES = {name.split()[0] for name in KNOWN_NAMES}
KNOWN_LAST_NAMES = {name.split()[-1] for name in KNOWN_NAMES}


def redact_pii(text: str, customer_id: str | None = None) -> tuple[str, dict]:
    """
    Redact PII from ticket text before sending it to an LLM.

    Returns:
        (redacted_text, pii_mapping) -- pii_mapping maps placeholder -> original value.
    """
    redacted = text
    pii_mapping: dict[str, str] = {}

    # 1. Emails
    for email in EMAIL_PATTERN.findall(redacted):
        pii_mapping["[EMAIL_REDACTED]"] = email
        redacted = redacted.replace(email, "[EMAIL_REDACTED]")

    # 2. Phone numbers
    for phone in PHONE_PATTERN.findall(redacted):
        pii_mapping["[PHONE_REDACTED]"] = phone
        redacted = redacted.replace(phone, "[PHONE_REDACTED]")

    # 3. Known full names -- longest first so "Sam" never breaks "Samantha Reed"
    for name in sorted(KNOWN_NAMES, key=len, reverse=True):
        if name in redacted:
            pii_mapping["[NAME_REDACTED]"] = name
            redacted = redacted.replace(name, "[NAME_REDACTED]")

    # 4. The ticket owner's first name on its own
    if customer_id and customer_id in CUSTOMERS_DB:
        full_name = CUSTOMERS_DB[customer_id]["name"]
        first_name = full_name.split()[0]
        if "[NAME_REDACTED]" not in pii_mapping and re.search(rf"\b{re.escape(first_name)}\b", redacted):
            pii_mapping["[NAME_REDACTED]"] = full_name
            redacted = re.sub(rf"\b{re.escape(first_name)}\b", "[NAME_REDACTED]", redacted)

    return redacted, pii_mapping


def restore_pii(text: str, pii_mapping: dict) -> str:
    """Put original values back. Only ever called on the FINAL customer-facing message."""
    restored = text
    for placeholder, original in pii_mapping.items():
        restored = restored.replace(placeholder, original)
    return restored
