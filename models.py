from pydantic import BaseModel

class TransactionData(BaseModel):
    user_id: str
    amount: float
    currency: str
    device_type: str
    location: str