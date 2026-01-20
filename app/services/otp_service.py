import secrets
from datetime import datetime, timedelta

def generate_otp() -> str:
    # Secure 6-digit OTP
    return str(secrets.randbelow(900000) + 100000)

def otp_expiry() -> datetime:
    return datetime.utcnow() + timedelta(minutes=5)


