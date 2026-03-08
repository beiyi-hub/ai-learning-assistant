from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
from services.settings_service import settings_service

# 加载环境变量
load_dotenv()

class AgentTeam:
    def __init__(self):
        # 从设置服务获取配置
        self._update_llm()
        
        # 初始化智能体的系统提示
        self.theory_tutor_system = "你是一个专业的理论导师，擅长解释各种概念和原理。你的任务是：1. 用清晰、简洁的语言解释复杂概念 2. 提供相关的例子来帮助理解 3. 确保解释的准确性和完整性 4. 回答用户的理论问题，不涉及实践代码或实验步骤"
        self.practice_coach_system = "你是一个专业的实践教练，擅长提供代码和实验步骤。你的任务是：1. 提供详细的代码示例和实验步骤 2. 确保代码的正确性和可执行性 3. 解释代码的工作原理 4. 回答用户的实践问题，不涉及纯理论解释"
        self.questioner_system = "你是一个专业的提问者，擅长提出启发式问题。你的任务是：1. 基于用户的学习内容提出深入的问题 2. 问题应该能够促进用户思考和理解 3. 问题应该具有启发性和挑战性 4. 不要直接回答问题，只提出问题"
    
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
    
    def get_agent_response(self, agent_name, message):
        """获取智能体的响应"""
        # 更新LLM配置（确保使用最新的设置）
        self._update_llm()
        
        # 根据智能体名称选择系统提示
        if agent_name == "理论导师":
            system_prompt = self.theory_tutor_system
        elif agent_name == "实践教练":
            system_prompt = self.practice_coach_system
        elif agent_name == "提问者":
            system_prompt = self.questioner_system
        else:
            return "未知智能体，请选择有效的智能体名称。"
        
        # 构建提示
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        
        # 格式化提示
        formatted_prompt = prompt.format_prompt(input=message).to_messages()
        
        # 获取响应
        response = self.llm(formatted_prompt)
        
        return response.content
    
    def reset_agents(self):
        """重置所有智能体的对话历史"""
        # 由于我们没有使用内存，所以这里不需要做任何操作
        pass