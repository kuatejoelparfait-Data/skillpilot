#!/usr/bin/env python3
"""Formateur: génère les clés de licence pour les étudiants."""
import sys
import hmac
import hashlib

SECRET = "REMPLACE_PAR_TON_SECRET_PERSONNEL"


def generate(email: str, year: int) -> str:
    payload = f"{email.lower().strip()}:{year}:{SECRET}"
    digest = hmac.new(
        key=SECRET.encode(),
        msg=payload.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return f"DEVPILOT-{digest[:8].upper()}-{year}"


if __name__ == "__main__":
    emails = sys.argv[1:] if len(sys.argv) > 1 else [input("Email étudiant: ")]
    year = 2026
    for email in emails:
        print(f"{email}: {generate(email, year)}")
