from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class LearningPathPhase(BaseModel):
    phase: str = Field(..., description="阶段编号")
    title: str = Field(..., description="阶段标题")
    description: str = Field(..., description="阶段描述")
    duration: str = Field(..., description="建议时长")

class ProjectStructure(BaseModel):
    recommended_agents: List[str] = Field(default_factory=list, description="推荐的智能体组合")
    learning_path: List[LearningPathPhase] = Field(default_factory=list, description="建议的学习路径")
    key_knowledge_points: List[str] = Field(default_factory=list, description="关键知识点清单")
    recommended_projects: List[str] = Field(default_factory=list, description="推荐的实践项目")

class ProjectBase(BaseModel):
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    topic: str = Field(..., description="Learning topic")

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str = Field(..., description="Project unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    agents: List[str] = Field(default_factory=list, description="List of agent names")
    progress: float = Field(default=0.0, description="Learning progress percentage")
    structure: Optional[ProjectStructure] = Field(default=None, description="Project structure and recommendations")
    
    class Config:
        orm_mode = True

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    progress: Optional[float] = None
