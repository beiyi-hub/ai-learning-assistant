from .agent_team import AgentTeam
import re

class AgentManager:
    def __init__(self):
        # 初始化智能体团队
        self.agent_team = AgentTeam()
    
    def process_message(self, message, context=""):
        """处理用户消息并返回智能体响应"""
        # 分析消息，提取@提及的智能体
        mentioned_agents = self._extract_mentioned_agents(message)
        
        # 如果没有提及特定智能体，默认使用理论导师
        if not mentioned_agents:
            mentioned_agents = ["理论导师"]
        
        # 获取每个提及的智能体的响应
        responses = []
        for agent in mentioned_agents:
            # 构建完整的消息上下文
            full_context = f"{context}\n用户: {message}"
            
            # 获取智能体响应
            response = self.agent_team.get_agent_response(agent, full_context)
            
            responses.append({
                "agent": agent,
                "content": response
            })
        
        return responses
    
    def _extract_mentioned_agents(self, message):
        """从消息中提取@提及的智能体"""
        # 定义智能体名称列表
        agent_names = ["理论导师", "实践教练", "提问者"]
        
        # 提取@提及的智能体
        mentioned_agents = []
        for agent in agent_names:
            if f"@{agent}" in message:
                mentioned_agents.append(agent)
        
        return mentioned_agents
    
    def reset_agents(self):
        """重置所有智能体的对话历史"""
        self.agent_team.reset_agents()

# 创建设置服务实例
tagent_manager = AgentManager()

# 为了兼容现有代码，创建一个别名
agent_manager = tagent_manager