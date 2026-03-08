from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MessageBase(BaseModel):
    content: str = Field(..., description="Message content")
    sender_type: str = Field(..., description="Sender type: user or agent")
    sender_name: str = Field(..., description="Sender name")

class MessageCreate(MessageBase):
    project_id: str = Field(..., description="Project ID associated with the message")

class Message(MessageBase):
    id: str = Field(..., description="Message unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    project_id: str = Field(..., description="Project ID associated with the message")
    
    class Config:
        orm_mode = True

class ChatHistory(BaseModel):
    project_id: str = Field(..., description="Project ID")
    messages: List[Message] = Field(default_factory=list, description="Chat history")
