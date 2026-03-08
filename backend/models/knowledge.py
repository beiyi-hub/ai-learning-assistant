from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class KnowledgeBaseItem(BaseModel):
    id: str = Field(..., description="Item unique identifier")
    project_id: str = Field(..., description="Project ID")
    type: str = Field(..., description="Item type: note, concept, confusion, interest")
    content: str = Field(..., description="Item content")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    tags: List[str] = Field(default_factory=list, description="List of tags")

class KnowledgeBaseItemCreate(BaseModel):
    project_id: str = Field(..., description="Project ID")
    type: str = Field(..., description="Item type: note, concept, confusion, interest")
    content: str = Field(..., description="Item content")
    tags: List[str] = Field(default_factory=list, description="List of tags")

class KnowledgeBaseSummary(BaseModel):
    project_id: str = Field(..., description="Project ID")
    total_items: int = Field(..., description="Total number of knowledge base items")
    concepts: int = Field(..., description="Number of concepts")
    confusions: int = Field(..., description="Number of confusion points")
    interests: int = Field(..., description="Number of interest points")
    notes: int = Field(..., description="Number of notes")

class KnowledgeRetrievalRequest(BaseModel):
    project_id: str = Field(..., description="Project ID")
    query: str = Field(..., description="Search query")
    limit: int = Field(default=5, description="Maximum number of results")

class KnowledgeRetrievalResult(BaseModel):
    items: List[KnowledgeBaseItem] = Field(..., description="Retrieved knowledge items")
    query: str = Field(..., description="Search query")
    project_id: str = Field(..., description="Project ID")
