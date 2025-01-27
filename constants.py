# constants.py

PHISHING_KEYWORDS = [
    # English
    "OTP", "KYC", "block", "suspend", "password", "account",
    "verify", "urgent", "winner", "bank", "security", "aadhaar",
    "lottery", "congratulations", "claim", "limited time", "offer",
    "click here", "update", "confirm", "login", "alert", "dear customer",
    "refund", "invoice", "transaction", "unauthorized", "immediate action",
    "act fast", "kindly", "request", "assistance", "help", "attention",
    "important", "notice", "payment", "due", "overdue", "access", "secure",
    "unusual activity", "suspicious", "locked", "unlock", "reactivate",
    "validate", "credentials", "personal information", "identity",
    "breach", "compromise", "security alert", "security update",
    "security notification", "security warning", "security message",
    "security advisory", "security notice",
    
    # Hindi
    "ओटीपी", "केवाईसी", "ब्लॉक", "निलंबित", "पासवर्ड", "खाता",
    "सत्यापित", "तत्काल", "विजेता", "बैंक", "सुरक्षा", "आधार",
    "लॉटरी", "बधाई", "दावा", "सीमित समय", "प्रस्ताव",
    "यहां क्लिक करें", "अपडेट", "पुष्टि", "लॉगिन", "चेतावनी", "प्रिय ग्राहक",
    "रिफंड", "चालान", "लेनदेन", "अनधिकृत", "तत्काल कार्रवाई",
    "शीघ्र करें", "कृपया", "अनुरोध", "सहायता", "मदद", "ध्यान",
    "महत्वपूर्ण", "सूचना", "भुगतान", "देय", "अतिदेय", "प्रवेश", "सुरक्षित",
    "असामान्य गतिविधि", "संदिग्ध", "लॉक", "अनलॉक", "पुनः सक्रिय करें",
    "मान्य करें", "क्रेडेंशियल्स", "व्यक्तिगत जानकारी", "पहचान",
    "उल्लंघन", "समझौता", "सुरक्षा चेतावनी", "सुरक्षा अपडेट",
    "सुरक्षा अधिसूचना", "सुरक्षा संदेश", "सुरक्षा सलाह", "सुरक्षा सूचना",
    
    # Hinglish
    "account band", "ATM card", "kyc update", "pan card",
    "password reset", "bank account", "kaun se bank ka account hai jisme paisa lena chahte ho",
]

FRAUD_PATTERNS = {
    "jamtara_scam": [
        "chhota amount", "multiple transfer", "jaldi karo",
        "aapka account block ho gaya hai"
    ],
    "vkyc_bypass": [
        "left dekh", "blink karo", "head ghuma"
    ],
    "lottery_scam": [
        "aap 25 lakh ka lottery jeete hain", "bank account mein paisa milega",
        "aapka number winner bana hai", "account number aur aadhaar card bhejein"
    ],
    "urgent_action": [
        "turant sampark karein", "abhi call karein", "fori tor par"
    ],
    "bank_verification": [
        "bank account verify karna hai", "aapka account suspend ho jayega",
        "kyc update karna hai"
    ]
}
