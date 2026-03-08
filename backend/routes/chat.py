from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import uuid
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from models.chat import Message, MessageCreate, ChatHistory
from agents.agent_manager import agent_manager

router = APIRouter()

# In-memory storage (will be replaced with database)
chat_history_db = {}

@router.post("/messages", response_model=List[Message])
async def send_message(message: MessageCreate):
    message_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    # 保存用户消息
    user_message = Message(
        id=message_id,
        created_at=now,
        **message.dict()
    )
    
    # Add user message to chat history
    if message.project_id not in chat_history_db:
        chat_history_db[message.project_id] = []
    chat_history_db[message.project_id].append(user_message)
    
    # 获取之前的聊天历史作为上下文
    context = "\n\n".join([f"{m.sender_name}: {m.content}" for m in chat_history_db[message.project_id][-10:]])  # 使用最近10条消息作为上下文
    
    # 处理消息并获取智能体响应
    agent_responses = agent_manager.process_message(message.content, context)
    
    # 保存智能体响应到聊天历史
    responses = [user_message]
    for i, agent_response in enumerate(agent_responses):
        agent_message_id = str(uuid.uuid4())
        agent_message = Message(
            id=agent_message_id,
            created_at=datetime.utcnow(),
            project_id=message.project_id,
            content=agent_response["content"],
            sender_type="agent",
            sender_name=agent_response["agent"]
        )
        chat_history_db[message.project_id].append(agent_message)
        responses.append(agent_message)
    
    return responses

@router.get("/projects/{project_id}/history", response_model=ChatHistory)
async def get_chat_history(project_id: str):
    if project_id not in chat_history_db:
        return ChatHistory(project_id=project_id, messages=[])
    return ChatHistory(project_id=project_id, messages=chat_history_db[project_id])

@router.delete("/projects/{project_id}/history")
async def clear_chat_history(project_id: str):
    if project_id in chat_history_db:
        del chat_history_db[project_id]
    return {"message": "Chat history cleared successfully"}
