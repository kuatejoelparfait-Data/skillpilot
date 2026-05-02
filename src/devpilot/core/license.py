import hmac
import hashlib

_DEFAULT_SECRET = "REPLACE_BEFORE_RELEASE_WITH_YOUR_OWN_SECRET"


def generate_license(email: str, year: int, secret: str = _DEFAULT_SECRET) -> str:
    payload = f"{email.lower().strip()}:{year}:{secret}"
    digest = hmac.new(
        key=secret.encode(),
        msg=payload.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
    token = digest[:8].upper()
    return f"DEVPILOT-{token}-{year}"


def validate_license(key: str, secret: str = _DEFAULT_SECRET) -> bool:
    try:
        parts = key.strip().split("-")
        if len(parts) != 3 or parts[0] != "DEVPILOT":
            return False
        token, year_str = parts[1], parts[2]
        if len(token) != 8 or not all(c in "0123456789ABCDEF" for c in token):
            return False
        int(year_str)
        return True
    except Exception:
        return False
