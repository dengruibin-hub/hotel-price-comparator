import re
import unicodedata


def normalize_text(value: str) -> str:
    """Normalize names/addresses for fuzzy matching."""
    value = unicodedata.normalize("NFKC", value or "").lower()
    value = re.sub(r"[\s\u3000]+", "", value)
    value = re.sub(r"[，。、“”‘’（）()【】\[\]{}<>·,./\\_-]+", "", value)
    return value


def normalize_phone(value: str) -> str:
    """Keep digits only so formatted phone numbers can be compared."""
    return re.sub(r"\D", "", value or "")
