from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    """Request model for /chat endpoint"""
    query: str = Field(..., description="User's question", min_length=1)
    user_email: Optional[str] = Field(
        default="john@example.com",
        description="User's email (for authentication in production)"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for conversation continuity"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Where is my order?",
                "user_email": "john@example.com",
                "session_id": "session_abc123def456"
            }
        }


class ChatResponse(BaseModel):
    """Response model for /chat endpoint"""
    success: bool = Field(..., description="Whether request was successful")
    query: str = Field(..., description="Original user query")
    intent: str = Field(..., description="Detected intent")
    data_source: str = Field(..., description="Where data was retrieved from")
    response: str = Field(..., description="AI-generated response")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata (entities, reasoning, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "query": "Where is my order?",
                "intent": "ORDER_DETAILS",
                "data_source": "SQL",
                "response": "You have two orders...",
                "metadata": {
                    "entities": {},
                    "reasoning": "User asking about order status"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(default=None, description="Detailed error info")