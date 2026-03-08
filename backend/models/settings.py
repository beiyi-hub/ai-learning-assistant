from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ModelSettings(BaseModel):
    """大模型设置"""
    provider: str = Field(default="openai", description="模型提供商")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    base_url: Optional[str] = Field(default=None, description="API基础URL")
    model_name: str = Field(default="gpt-3.5-turbo", description="模型名称")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0, description="温度参数")
    max_tokens: int = Field(default=1000, ge=1, le=4096, description="最大令牌数")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="Top P参数")
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="频率惩罚")
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="存在惩罚")

class AppSettings(BaseModel):
    """应用设置"""
    id: str = Field(default="default", description="设置ID")
    model_settings: ModelSettings = Field(default_factory=ModelSettings, description="大模型设置")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")

class SettingsUpdate(BaseModel):
    """更新设置的请求模型"""
    model_settings: Optional[ModelSettings] = Field(default=None, description="大模型设置")
