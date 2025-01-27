from fastapi import APIRouter  
from pydantic import BaseModel  
import boto3  

router = APIRouter()  

class Feedback(BaseModel):  
    session_id: str  
    is_fraud: bool  

@router.post("/report")  
def submit_feedback(feedback: Feedback):  
    # Store in DynamoDB  
    dynamodb = boto3.resource('dynamodb')  
    table = dynamodb.Table('fraud_feedback')  
    table.put_item(Item=feedback.dict())  