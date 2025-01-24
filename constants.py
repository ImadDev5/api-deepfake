# constants.py
PHISHING_KEYWORDS = [
    "OTP", "KYC", "block", "suspend", "password", "account", 
    "verify", "urgent", "immediately", "winner", "prize", "bank",
    "security", "update", "aadhaar", "pan", "kyc", "card", "upi"
]

FRAUD_PATTERNS = {
    "jamtara_scam": ["small amounts", "multiple transfers", "urgent"],
    "vkyc_bypass": ["look left", "blink twice", "turn head"]
}