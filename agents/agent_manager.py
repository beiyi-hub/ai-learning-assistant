import re
import os
import sys
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 添加后端目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from langchain.chat_models import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

from agents.config import AGENT_CONFIGS, COLLABORATION_RULES
from services.settings_service import settings_service

# 加载环境变量
load_dotenv()

class AgentManager:
    def __init__(self):
        self.agents = {}
        self.group_chats = {}
        self.agent_configs = AGENT_CONFIGS
        self.collaboration_rules = COLLABORATION_RULES
        
        # 获取当前设置
        self.settings = settings_service.get_settings()
        
        # 初始化所有智能体
        self._initialize_agents()
    
    def _initialize_agents(self):
        """初始化所有智能体"""
        # 确保使用最新的设置
        self.settings = settings_service.get_settings()
        
        for agent_name, config in self.agent_configs.items():
            self.agents[agent_name] = {
                "config": config,
                "llm_chain": self._create_llm_chain(agent_name, config)
            }
    
    def _create_llm_chain(self, agent_name: str, config: Dict[str, Any]):
        """创建LLM链"""
        # 获取当前大模型设置
        model_settings = self.settings.model_settings
        
        # 从环境变量获取配置
        api_key = os.getenv('OPENAI_API_KEY', model_settings.api_key)
        base_url = os.getenv('BASE_URL', model_settings.base_url)
        model_name = os.getenv('MODEL_NAME', model_settings.model_name)
        
        # 如果有API密钥，使用真实的OpenAI模型
        if api_key:
            system_prompt = SystemMessagePromptTemplate.from_template(config["system_prompt"])
            human_prompt = HumanMessagePromptTemplate.from_template("{input}")
            chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
            
            # 使用当前设置创建ChatOpenAI实例
            llm = ChatOpenAI(
                model=model_name,
                temperature=model_settings.temperature,
                max_tokens=model_settings.max_tokens,
                api_key=api_key,
                base_url=base_url,
                top_p=model_settings.top_p,
                frequency_penalty=model_settings.frequency_penalty,
                presence_penalty=model_settings.presence_penalty
            )
            
            return LLMChain(llm=llm, prompt=chat_prompt)
        else:
            # 如果没有API密钥，返回模拟的LLM链
            class MockLLMChain:
                def __init__(self, system_prompt):
                    self.system_prompt = system_prompt
                    self.agent_name = agent_name
                    self.config = config
                    self.model_settings = model_settings
                
                def run(self, input):
                    # 返回模拟的智能体响应，包含当前设置信息
                    mock_responses = {
                        "理论导师": f"[理论导师模拟响应] 针对您的问题：{input} (使用模型: {model_name}, 温度: {self.model_settings.temperature})",
                        "数据分析师": f"[数据分析师模拟响应] 针对您的问题：{input} (使用模型: {model_name}, 温度: {self.model_settings.temperature})",
                        "实践教练": f"[实践教练模拟响应] 针对您的问题：{input} (使用模型: {model_name}, 温度: {self.model_settings.temperature})",
                        "提问专家": f"[提问专家模拟响应] 针对您的问题：{input} (使用模型: {model_name}, 温度: {self.model_settings.temperature})",
                        "历史记录员": f"[历史记录员模拟响应] 针对您的问题：{input} (使用模型: {model_name}, 温度: {self.model_settings.temperature})"
                    }
                    return mock_responses.get(self.agent_name, f"[模拟响应] {input}")
            
            return MockLLMChain(config["system_prompt"])
    
    def get_agent_response(self, agent_name: str, user_input: str, context: Optional[str] = None) -> str:
        """获取单个智能体的响应"""
        if agent_name not in self.agents:
            return f"未找到智能体: {agent_name}"
        
        # 如果有上下文，将其添加到输入中
        if context:
            full_input = f"上下文: {context}\n\n用户问题: {user_input}"
        else:
            full_input = user_input
        
        result = self.agents[agent_name]["llm_chain"].run(input=full_input)
        return result
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """分析用户查询，确定需要的智能体和协作顺序"""
        # 检查是否@了特定智能体
        agent_mentions = re.findall(r"@([^\s]+)", query)
        
        if agent_mentions:
            # 如果提到了特定智能体，直接使用该智能体
            return {
                "type": "direct",
                "target_agent": agent_mentions[0],
                "clean_query": re.sub(r"@[^\s]+\s*", "", query).strip()
            }
        else:
            # 根据查询模式确定协作序列
            for rule_name, rule in self.collaboration_rules.items():
                for pattern in rule["trigger_patterns"]:
                    if re.search(pattern, query, re.IGNORECASE):
                        return {
                            "type": "collaboration",
                            "rule_name": rule_name,
                            "agent_sequence": rule["sequence"],
                            "query": query
                        }
            
            # 默认使用理论导师
            return {
                "type": "default",
                "target_agent": "理论导师",
                "query": query
            }
    
    def process_message(self, query: str, context: Optional[str] = None) -> List[Dict[str, str]]:
        """处理用户消息，返回智能体的响应"""
        analysis_result = self.analyze_query(query)
        responses = []
        
        if analysis_result["type"] == "direct":
            # 直接调用特定智能体
            agent_name = analysis_result["target_agent"]
            if agent_name in self.agents:
                response = self.get_agent_response(agent_name, analysis_result["clean_query"], context)
                responses.append({
                    "agent": agent_name,
                    "content": response
                })
        elif analysis_result["type"] == "collaboration":
            # 智能体协作
            current_context = context
            for agent_name in analysis_result["agent_sequence"]:
                if agent_name in self.agents:
                    response = self.get_agent_response(agent_name, analysis_result["query"], current_context)
                    responses.append({
                        "agent": agent_name,
                        "content": response
                    })
                    # 将上一个智能体的响应作为下一个智能体的上下文
                    current_context = response
        else:
            # 默认情况
            agent_name = analysis_result["target_agent"]
            if agent_name in self.agents:
                response = self.get_agent_response(agent_name, analysis_result["query"], context)
                responses.append({
                    "agent": agent_name,
                    "content": response
                })
        
        return responses
    
    def get_agent_info(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """获取智能体信息"""
        if agent_name:
            if agent_name in self.agents:
                return self.agents[agent_name]["config"]
            else:
                return {"error": f"未找到智能体: {agent_name}"}
        else:
            # 返回所有智能体信息
            return {name: agent["config"] for name, agent in self.agents.items()}

# 创建全局智能体管理器实例
agent_manager = AgentManager()
