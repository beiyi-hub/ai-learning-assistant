from typing import Dict, Any, Optional
from models.settings import AppSettings, ModelSettings

class SettingsService:
    """设置服务，用于管理和获取应用设置"""
    
    def __init__(self):
        # 默认设置
        self._settings = AppSettings(
            id="default",
            model_settings=ModelSettings(
                provider="openai",
                api_key=None,
                base_url=None,
                model_name="gpt-3.5-turbo",
                temperature=0.3,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
        )
    
    def get_settings(self) -> AppSettings:
        """获取当前设置"""
        return self._settings
    
    def update_settings(self, settings: AppSettings) -> AppSettings:
        """更新设置"""
        self._settings = settings
        return self._settings
    
    def get_model_settings(self) -> ModelSettings:
        """获取大模型设置"""
        return self._settings.model_settings
    
    def update_model_settings(self, model_settings: ModelSettings) -> ModelSettings:
        """更新大模型设置"""
        self._settings.model_settings = model_settings
        return self._settings.model_settings

# 创建全局设置服务实例
settings_service = SettingsService()
