import os
import sys
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from typing import List, Dict, Any
from datetime import datetime

# 添加后端目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from services.settings_service import settings_service

class DailySummaryService:
    def __init__(self):
        """初始化每日学习总结服务"""
        # 获取当前设置
        self.settings = settings_service.get_settings()
        
        # 总结生成提示
        self.summary_prompt = ChatPromptTemplate.from_template(
            """
            你是一位学习助手，负责根据用户与AI智能体的对话记录生成每日学习总结。
            请分析以下对话记录，生成一份结构化的学习总结：
            
            对话记录：
            {conversation_history}
            
            总结应包含以下部分：
            1. 今日学习主题
            2. 核心概念与定义（由理论导师提取）
            3. 关键代码与实践步骤（由实践教练整理）
            4. 待复习的疑惑点（标记用户反复提问或不确定的内容）
            5. 用户感兴趣的话题（根据用户的追问深度和积极反馈标记）
            6. 明日学习建议
            
            请以JSON格式输出，确保格式正确。
            输出格式：
            {{
                "today_date": "YYYY-MM-DD",
                "learning_topic": "今日学习主题",
                "core_concepts": [
                    {{"concept": "概念名称", "definition": "概念定义"}},
                    ...
                ],
                "key_practices": [
                    {{"title": "实践内容", "content": "详细说明或代码"}},
                    ...
                ],
                "confusion_points": [
                    {{"content": "疑惑内容", "context": "出现上下文"}},
                    ...
                ],
                "interest_topics": [
                    {{"topic": "兴趣话题", "reason": "标记原因"}},
                    ...
                ],
                "tomorrow_suggestions": ["建议1", "建议2", ...]
            }}
            """
        )
    
    def _generate_mock_summary(self, conversation_history):
        """生成模拟的每日学习总结"""
        # 获取当前大模型设置
        model_settings = self.settings.model_settings
        
        return {
            "today_date": datetime.now().strftime("%Y-%m-%d"),
            "learning_topic": "Python编程学习",
            "core_concepts": [
                {"concept": "函数", "definition": "函数是组织好的、可重复使用的、用来实现单一或相关联功能的代码段。"},
                {"concept": "列表", "definition": "列表是Python中用于存储多个元素的可变序列数据类型。"}
            ],
            "key_practices": [
                {"title": "函数定义与调用", "content": "def greet(name):\n    return f'Hello, {name}! '\n\nprint(greet('World'))"},
                {"title": "列表操作", "content": "numbers = [1, 2, 3, 4, 5]\nprint(numbers[0])  # 访问第一个元素\nnumbers.append(6)  # 添加元素"}
            ],
            "confusion_points": [
                {"content": "函数参数传递", "context": "用户询问关于传值和传引用的区别"}
            ],
            "interest_topics": [
                {"topic": "面向对象编程", "reason": "用户多次追问类和对象的概念"}
            ],
            "tomorrow_suggestions": [
                "学习面向对象编程的基本概念",
                "练习使用类和对象进行编程",
                "阅读关于Python设计模式的资料"
            ]
        }
    
    def generate_summary(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """生成每日学习总结"""
        # 确保使用最新的设置
        self.settings = settings_service.get_settings()
        model_settings = self.settings.model_settings
        
        try:
            # 如果有API密钥，使用真实的OpenAI模型
            if model_settings.api_key:
                # 创建LLM链
                llm = ChatOpenAI(
                    model=model_settings.model_name,
                    temperature=model_settings.temperature,
                    max_tokens=model_settings.max_tokens,
                    api_key=model_settings.api_key,
                    base_url=model_settings.base_url,
                    top_p=model_settings.top_p,
                    frequency_penalty=model_settings.frequency_penalty,
                    presence_penalty=model_settings.presence_penalty
                )
                
                summary_chain = LLMChain(llm=llm, prompt=self.summary_prompt)
                
                # 将对话历史转换为文本格式
                history_text = "\n\n".join([f"{msg['sender_name']}: {msg['content']}" for msg in conversation_history])
                
                # 调用LLM生成总结
                result = summary_chain.run(conversation_history=history_text)
                
                # 解析JSON结果
                import json
                summary = json.loads(result)
                
                # 确保日期格式正确
                if "today_date" not in summary or not summary["today_date"]:
                    summary["today_date"] = datetime.now().strftime("%Y-%m-%d")
                
                # 确保各部分都存在
                required_fields = ["core_concepts", "key_practices", "confusion_points", "interest_topics", "tomorrow_suggestions"]
                for field in required_fields:
                    if field not in summary or not isinstance(summary[field], list):
                        summary[field] = []
                
                return summary
            else:
                # 如果没有API密钥，使用模拟的总结生成器
                return self._generate_mock_summary(conversation_history)
        except Exception as e:
            print(f"生成每日总结失败: {e}")
            # 返回默认总结
            return {
                "today_date": datetime.now().strftime("%Y-%m-%d"),
                "learning_topic": "今日学习内容",
                "core_concepts": [],
                "key_practices": [],
                "confusion_points": [],
                "interest_topics": [],
                "tomorrow_suggestions": []
            }
    
    def save_summary_to_knowledge_base(self, project_id: str, summary: Dict[str, Any], vector_db_manager):
        """将总结保存到知识库"""
        try:
            # 创建总结内容
            summary_content = f"# 每日学习总结 - {summary['today_date']}\n\n"
            summary_content += f"## 今日学习主题\n{summary['learning_topic']}\n\n"
            
            if summary['core_concepts']:
                summary_content += "## 核心概念与定义\n"
                for concept in summary['core_concepts']:
                    summary_content += f"### {concept['concept']}\n{concept['definition']}\n\n"
            
            if summary['key_practices']:
                summary_content += "## 关键代码与实践步骤\n"
                for practice in summary['key_practices']:
                    summary_content += f"### {practice['title']}\n{practice['content']}\n\n"
            
            if summary['confusion_points']:
                summary_content += "## 待复习的疑惑点\n"
                for confusion in summary['confusion_points']:
                    summary_content += f"- {confusion['content']}\n"
                summary_content += "\n"
            
            if summary['interest_topics']:
                summary_content += "## 感兴趣的话题\n"
                for interest in summary['interest_topics']:
                    summary_content += f"- {interest['topic']} ({interest['reason']})\n"
                summary_content += "\n"
            
            if summary['tomorrow_suggestions']:
                summary_content += "## 明日学习建议\n"
                for suggestion in summary['tomorrow_suggestions']:
                    summary_content += f"- {suggestion}\n"
                summary_content += "\n"
            
            # 添加到向量数据库
            metadata = {
                "type": "summary",
                "date": summary['today_date'],
                "tags": ["daily_summary", "learning_summary"] + [concept['concept'] for concept in summary['core_concepts'][:5]]
            }
            
            doc_id = vector_db_manager.add_document(
                content=summary_content,
                metadata=metadata,
                project_id=project_id
            )
            
            # 保存每个核心概念作为单独的知识库条目
            for concept in summary['core_concepts']:
                concept_content = f"# {concept['concept']}\n\n{concept['definition']}"
                concept_metadata = {
                    "type": "concept",
                    "date": summary['today_date'],
                    "tags": ["concept", concept['concept'].lower()]
                }
                vector_db_manager.add_document(
                    content=concept_content,
                    metadata=concept_metadata,
                    project_id=project_id
                )
            
            # 保存疑惑点作为单独的知识库条目
            for i, confusion in enumerate(summary['confusion_points']):
                confusion_content = f"# 疑惑点 #{i+1}\n\n{confusion['content']}\n\n上下文：{confusion['context']}"
                confusion_metadata = {
                    "type": "confusion",
                    "date": summary['today_date'],
                    "tags": ["confusion", "to_review"]
                }
                vector_db_manager.add_document(
                    content=confusion_content,
                    metadata=confusion_metadata,
                    project_id=project_id
                )
            
            return doc_id
        except Exception as e:
            print(f"保存总结到知识库失败: {e}")
            return None

# 创建全局每日学习总结服务实例
daily_summary_service = DailySummaryService()
