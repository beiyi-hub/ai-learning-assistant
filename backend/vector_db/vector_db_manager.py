import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class VectorDBManager:
    def __init__(self):
        # 暂时注释掉ChromaDB初始化，避免Python版本兼容性问题
        # 后续可以在Python 3.9+环境中取消注释
        # import chromadb
        # from chromadb.config import Settings
        # self.client = chromadb.Client(Settings(
        #     persist_directory=os.getenv("CHROMA_DB_PATH", "./vector_db"),
        #     anonymized_telemetry=False
        # ))
        # self.collection = self.client.get_or_create_collection(name="knowledge_base")
        pass
    
    def add_document(self, content, metadata, project_id):
        """添加文档到向量数据库"""
        # 生成文档ID
        doc_id = f"{project_id}_{metadata['date'] if 'date' in metadata else 'unknown'}"
        
        # 暂时返回文档ID，不实际存储
        return doc_id
    
    def search_documents(self, query, project_id, limit=5):
        """搜索相关文档"""
        # 暂时返回空结果，后续可以实现向量搜索
        return []
    
    def delete_document(self, doc_id):
        """删除文档"""
        # 暂时不做任何操作
        pass
    
    def get_collection_stats(self):
        """获取集合统计信息"""
        # 暂时返回0
        return 0

# 创建设置服务实例
vector_db_manager = VectorDBManager()