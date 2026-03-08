from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import uuid
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from models.knowledge import (
    KnowledgeBaseItem, 
    KnowledgeBaseItemCreate, 
    KnowledgeBaseSummary,
    KnowledgeRetrievalRequest,
    KnowledgeRetrievalResult
)
# 导入向量数据库管理器
from vector_db.vector_db_manager import vector_db_manager
from knowledge_base.daily_summary import daily_summary_service

# 导入聊天历史数据库（实际应用中应该从数据库或服务中获取）
from routes.chat import chat_history_db  # 修复导入路径

router = APIRouter()

# 添加每日学习总结的API接口
@router.post("/projects/{project_id}/daily-summary", response_model=Dict[str, Any])
async def generate_daily_summary(project_id: str):
    """生成每日学习总结"""
    try:
        # 获取项目的聊天历史
        if project_id not in chat_history_db or not chat_history_db[project_id]:
            raise HTTPException(status_code=404, detail="没有找到聊天历史记录")
        
        # 调用每日总结服务生成总结
        summary = daily_summary_service.generate_summary(chat_history_db[project_id])
        
        # 保存总结到知识库
        doc_id = daily_summary_service.save_summary_to_knowledge_base(project_id, summary, vector_db_manager)
        
        # 添加文档ID到总结结果
        summary["document_id"] = doc_id
        
        return summary
    except HTTPException:
        raise
    except Exception as e:
        print(f"生成每日总结失败: {e}")
        raise HTTPException(status_code=500, detail="生成每日总结失败")

# In-memory storage (will be replaced with vector database)
knowledge_base_db = []

@router.post("/items", response_model=KnowledgeBaseItem)
async def add_knowledge_item(item: KnowledgeBaseItemCreate):
    item_id = str(uuid.uuid4())
    now = datetime.utcnow()
    new_item = KnowledgeBaseItem(
        id=item_id,
        created_at=now,
        updated_at=now,
        **item.dict()
    )
    
    # 添加到内存存储（临时）
    knowledge_base_db.append(new_item)
    
    # 添加到向量数据库
    metadata = {
        "type": item.type,
        "tags": item.tags,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    vector_db_manager.add_document(
        content=item.content,
        metadata=metadata,
        project_id=item.project_id
    )
    
    return new_item

@router.get("/projects/{project_id}/items", response_model=List[KnowledgeBaseItem])
async def get_project_knowledge(project_id: str):
    return [item for item in knowledge_base_db if item.project_id == project_id]

@router.get("/projects/{project_id}/summary", response_model=KnowledgeBaseSummary)
async def get_knowledge_summary(project_id: str):
    project_items = [item for item in knowledge_base_db if item.project_id == project_id]
    total_items = len(project_items)
    concepts = len([item for item in project_items if item.type == "concept"])
    confusions = len([item for item in project_items if item.type == "confusion"])
    interests = len([item for item in project_items if item.type == "interest"])
    notes = len([item for item in project_items if item.type == "note"])
    
    return KnowledgeBaseSummary(
        project_id=project_id,
        total_items=total_items,
        concepts=concepts,
        confusions=confusions,
        interests=interests,
        notes=notes
    )

@router.post("/retrieve", response_model=KnowledgeRetrievalResult)
async def retrieve_knowledge(request: KnowledgeRetrievalRequest):
    try:
        # 使用向量数据库进行搜索
        search_results = vector_db_manager.search_documents(
            query=request.query,
            project_id=request.project_id,
            limit=request.limit
        )
        
        # 将搜索结果转换为KnowledgeBaseItem格式
        results = []
        for result in search_results:
            # 这里简化处理，实际项目中可能需要更复杂的转换
            item = KnowledgeBaseItem(
                id=result['metadata'].get('id', 'unknown'),
                project_id=request.project_id,
                content=result['content'],
                type=result['metadata'].get('type', 'note'),
                tags=result['metadata'].get('tags', []),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            results.append(item)
        
        # 结合内存存储中的数据，确保结果完整
        project_items = [item for item in knowledge_base_db if item.project_id == request.project_id]
        query_lower = request.query.lower()
        for item in project_items:
            if query_lower in item.content.lower() or any(query_lower in tag.lower() for tag in item.tags):
                if not any(result.id == item.id for result in results):
                    results.append(item)
        
        # Return top N results
        return KnowledgeRetrievalResult(
            items=results[:request.limit],
            query=request.query,
            project_id=request.project_id
        )
    except Exception as e:
        # 如果搜索失败，返回空结果
        print(f"搜索失败: {e}")
        return KnowledgeRetrievalResult(
            items=[],
            query=request.query,
            project_id=request.project_id
        )

@router.delete("/items/{item_id}")
async def delete_knowledge_item(item_id: str):
    global knowledge_base_db
    original_length = len(knowledge_base_db)
    knowledge_base_db = [item for item in knowledge_base_db if item.id != item_id]
    
    if len(knowledge_base_db) == original_length:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    
    return {"message": "Knowledge item deleted successfully"}
