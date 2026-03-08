from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import uuid
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from models.project import Project, ProjectCreate, ProjectUpdate, ProjectStructure
from agents.project_initializer import project_initializer

router = APIRouter()

# In-memory storage (will be replaced with database)
projects_db = {}

@router.post("/", response_model=Project)
async def create_project(project: ProjectCreate):
    project_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    # 初始化项目结构
    project_structure = project_initializer.initialize_project(
        topic=project.topic,
        description=project.description
    )
    
    # 从项目结构中获取推荐智能体
    recommended_agents = project_structure.get("recommended_agents", ["理论导师", "实践教练"])
    
    # 创建项目结构对象
    structure = ProjectStructure(
        recommended_agents=recommended_agents,
        learning_path=project_structure.get("learning_path", []),
        key_knowledge_points=project_structure.get("key_knowledge_points", []),
        recommended_projects=project_structure.get("recommended_projects", [])
    )
    
    new_project = Project(
        id=project_id,
        created_at=now,
        updated_at=now,
        agents=recommended_agents,
        structure=structure,
        **project.dict()
    )
    projects_db[project_id] = new_project
    return new_project

@router.get("/", response_model=List[Project])
async def get_all_projects():
    return list(projects_db.values())

@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects_db[project_id]

@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, project_update: ProjectUpdate):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    project = projects_db[project_id]
    update_data = project_update.dict(exclude_unset=True)
    updated_project = project.copy(update=update_data)
    updated_project.updated_at = datetime.utcnow()
    projects_db[project_id] = updated_project
    return updated_project

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    del projects_db[project_id]
    return {"message": "Project deleted successfully"}
