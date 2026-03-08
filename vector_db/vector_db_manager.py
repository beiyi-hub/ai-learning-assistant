import chromadb
from chromadb.utils import embedding_functions
import uuid
import os
from typing import List, Dict, Any, Optional

class VectorDBManager:
    def __init__(self, db_path: str = "../vector_db"):
        """初始化向量数据库"""
        # 确保数据库路径存在
        os.makedirs(db_path, exist_ok=True)
        
        # 创建ChromaDB客户端（使用新版本的API）
        self.client = chromadb.PersistentClient(path=db_path)
        
        # 使用默认的嵌入函数
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # 创建或获取知识库集合
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_document(self, content: str, metadata: Dict[str, Any], project_id: str) -> str:
        """添加文档到向量数据库"""
        doc_id = str(uuid.uuid4())
        
        # 添加文档元数据
        metadata["project_id"] = project_id
        metadata["doc_id"] = doc_id
        
        # 添加到集合
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        return doc_id
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """批量添加文档到向量数据库"""
        if not documents:
            return []
        
        contents = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        doc_ids = [str(uuid.uuid4()) for _ in documents]
        
        # 添加文档元数据
        for i, metadata in enumerate(metadatas):
            metadata["doc_id"] = doc_ids[i]
        
        # 添加到集合
        self.collection.add(
            documents=contents,
            metadatas=metadatas,
            ids=doc_ids
        )
        
        return doc_ids
    
    def search_documents(self, query: str, project_id: str, limit: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """搜索相关文档"""
        # 构建过滤条件
        search_filters = {"project_id": project_id}
        if filters:
            search_filters.update(filters)
        
        # 搜索文档
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=search_filters
        )
        
        # 格式化结果
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        
        return formatted_results
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """获取单个文档"""
        results = self.collection.get(
            ids=[doc_id]
        )
        
        if not results["ids"]:
            return None
        
        return {
            "id": results["ids"][0],
            "content": results["documents"][0],
            "metadata": results["metadatas"][0]
        }
    
    def update_document(self, doc_id: str, content: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """更新文档"""
        # 获取当前文档
        current_doc = self.get_document(doc_id)
        if not current_doc:
            return False
        
        # 更新内容
        if content is not None:
            self.collection.update(
                ids=[doc_id],
                documents=[content]
            )
        
        # 更新元数据
        if metadata is not None:
            # 合并新的元数据到现有元数据
            updated_metadata = current_doc["metadata"]
            updated_metadata.update(metadata)
            
            self.collection.update(
                ids=[doc_id],
                metadatas=[updated_metadata]
            )
        
        return True
    
    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"删除文档失败: {e}")
            return False
    
    def delete_project_documents(self, project_id: str) -> bool:
        """删除特定项目的所有文档"""
        try:
            # 先获取项目的所有文档ID
            results = self.collection.get(
                where={"project_id": project_id}
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
            
            return True
        except Exception as e:
            print(f"删除项目文档失败: {e}")
            return False
    
    def get_project_stats(self, project_id: str) -> Dict[str, int]:
        """获取项目的文档统计信息"""
        results = self.collection.get(
            where={"project_id": project_id}
        )
        
        # 统计不同类型的文档
        type_counts = {}
        for metadata in results["metadatas"]:
            doc_type = metadata.get("type", "unknown")
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        return {
            "total_documents": len(results["ids"]),
            "type_counts": type_counts
        }

# 创建全局向量数据库管理器实例
vector_db_manager = VectorDBManager()
