from fastapi import APIRouter, HTTPException
from datetime import datetime

from models.settings import AppSettings, SettingsUpdate
from services.settings_service import settings_service

router = APIRouter()

@router.get("/", response_model=AppSettings)
async def get_settings():
    """获取当前应用设置"""
    try:
        return settings_service.get_settings()
    except Exception as e:
        print(f"获取设置失败: {e}")
        raise HTTPException(status_code=500, detail="获取设置失败")

@router.put("/", response_model=AppSettings)
async def update_settings(settings_update: SettingsUpdate):
    """更新应用设置"""
    try:
        current_settings = settings_service.get_settings()
        
        if settings_update.model_settings:
            # 更新模型设置
            current_settings.model_settings = settings_update.model_settings
        
        # 更新时间戳
        current_settings.updated_at = datetime.utcnow()
        
        # 保存到设置服务
        updated_settings = settings_service.update_settings(current_settings)
        
        return updated_settings
    except Exception as e:
        print(f"更新设置失败: {e}")
        raise HTTPException(status_code=500, detail="更新设置失败")
