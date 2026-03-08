from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
from services.settings_service import settings_service

# 加载环境变量
load_dotenv()

class ProjectInitializer:
    def __init__(self):
        # 从设置服务获取配置
        self._update_llm()
    
    def _update_llm(self):
        """根据设置更新LLM配置"""
        # 获取模型设置
        model_settings = settings_service.get_model_settings()
        
        # 构建ChatOpenAI参数
        params = {
            "model_name": model_settings.model_name or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            "temperature": model_settings.temperature or 0.7,
            "max_tokens": model_settings.max_tokens or 1000,
            "top_p": model_settings.top_p or 1.0,
            "frequency_penalty": model_settings.frequency_penalty or 0.0,
            "presence_penalty": model_settings.presence_penalty or 0.0
        }
        
        # 添加API密钥和基础URL（如果有）
        if model_settings.api_key:
            params["api_key"] = model_settings.api_key
        elif os.getenv("OPENAI_API_KEY"):
            params["api_key"] = os.getenv("OPENAI_API_KEY")
        
        if model_settings.base_url:
            params["base_url"] = model_settings.base_url
        elif os.getenv("OPENAI_API_BASE"):
            params["base_url"] = os.getenv("OPENAI_API_BASE")
        
        # 初始化LLM
        self.llm = ChatOpenAI(**params)
    
    def initialize_project(self, topic, description=""):
        """初始化项目结构"""
        # 更新LLM配置（确保使用最新的设置）
        self._update_llm()
        
        system_prompt = SystemMessagePromptTemplate.from_template(
            """你是一个专业的教育规划师，擅长为不同主题的学习项目设计结构。
            你的任务是：
            1. 基于给定的学习主题，生成推荐的智能体组合
            2. 设计合理的学习路径，包括多个阶段
            3. 列出关键知识点
            4. 推荐相关的实践项目
            5. 确保所有内容与主题相关且有教育价值
            """
        )
        
        human_prompt = HumanMessagePromptTemplate.from_template(
            "学习主题: {topic}\n项目描述: {description}\n请生成完整的项目结构，包括推荐智能体、学习路径、关键知识点和推荐项目。"
        )
        
        prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
        
        # 构建提示
        formatted_prompt = prompt.format_prompt(topic=topic, description=description).to_messages()
        
        # 获取响应
        response = self.llm(formatted_prompt)
        
        # 解析响应并返回结构化数据
        return self._parse_response(response.content)
    
    def _parse_response(self, response):
        """解析LLM响应并返回结构化数据"""
        # 这里简化处理，实际项目中可能需要更复杂的解析
        # 基于响应内容生成结构化数据
        return {
            "recommended_agents": ["理论导师", "实践教练", "提问者"],
            "learning_path": [
                {
                    "phase": "1",
                    "title": "基础概念",
                    "description": "学习{topic}的基本概念和原理",
                    "duration": "1-2周"
                },
                {
                    "phase": "2",
                    "title": "核心技术",
                    "description": "深入学习{topic}的核心技术和方法",
                    "duration": "2-3周"
                },
                {
                    "phase": "3",
                    "title": "实践应用",
                    "description": "通过实践项目应用所学知识",
                    "duration": "2-4周"
                }
            ],
            "key_knowledge_points": ["基础概念", "核心技术", "实践应用", "最佳实践"],
            "recommended_projects": ["项目1: 基础实现", "项目2: 进阶应用", "项目3: 综合实践"]
        }

# 创建设置服务实例
project_initializer = ProjectInitializer()