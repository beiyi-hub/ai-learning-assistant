from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
from services.settings_service import settings_service

# 加载环境变量
load_dotenv()

class DailySummaryService:
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
    
    def generate_summary(self, chat_history):
        """生成每日学习总结"""
        # 更新LLM配置（确保使用最新的设置）
        self._update_llm()
        
        # 构建聊天历史文本
        chat_text = "\n".join([f"{msg.sender_name}: {msg.content}" for msg in chat_history])
        
        system_prompt = SystemMessagePromptTemplate.from_template(
            """你是一个专业的学习助手，擅长总结学习内容。
            你的任务是：
            1. 分析用户和智能体的对话历史
            2. 生成精简的学习笔记，包括核心概念和重要内容
            3. 识别用户的疑惑点（反复提问的内容）
            4. 识别用户的兴趣点（追问较多的内容）
            5. 确保总结全面且准确
            """
        )
        
        human_prompt = HumanMessagePromptTemplate.from_template(
            "以下是今日的学习对话历史：\n{chat_history}\n请生成每日学习总结，包括：\n1. 精简笔记（核心概念、重要内容）\n2. 疑惑点标记\n3. 兴趣点标记"
        )
        
        prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
        
        # 构建提示
        formatted_prompt = prompt.format_prompt(chat_history=chat_text).to_messages()
        
        # 获取响应
        response = self.llm(formatted_prompt)
        
        # 解析响应并返回结构化数据
        return self._parse_response(response.content)
    
    def _parse_response(self, response):
        """解析LLM响应并返回结构化数据"""
        # 这里简化处理，实际项目中可能需要更复杂的解析
        return {
            "date": datetime.now().isoformat(),
            "notes": response,
            "confusion_points": ["需要进一步理解的概念1", "需要进一步理解的概念2"],
            "interest_points": ["用户感兴趣的主题1", "用户感兴趣的主题2"]
        }
    
    def save_summary_to_knowledge_base(self, project_id, summary, vector_db_manager):
        """保存总结到知识库"""
        # 构建文档内容
        document_content = f"日期: {summary['date']}\n\n笔记: {summary['notes']}\n\n疑惑点: {', '.join(summary['confusion_points'])}\n\n兴趣点: {', '.join(summary['interest_points'])}"
        
        # 构建元数据
        metadata = {
            "project_id": project_id,
            "date": summary['date'],
            "type": "daily_summary",
            "confusion_points": summary['confusion_points'],
            "interest_points": summary['interest_points']
        }
        
        # 保存到向量数据库
        doc_id = vector_db_manager.add_document(
            content=document_content,
            metadata=metadata,
            project_id=project_id
        )
        
        return doc_id

# 创建设置服务实例
daily_summary_service = DailySummaryService()