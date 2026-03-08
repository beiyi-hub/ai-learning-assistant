import axios from 'axios';

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 项目管理API
export const projectApi = {
  // 创建项目
  createProject: (projectData) => apiClient.post('/projects', projectData),
  // 获取所有项目
  getProjects: () => apiClient.get('/projects'),
  // 获取单个项目
  getProject: (projectId) => apiClient.get(`/projects/${projectId}`),
  // 更新项目
  updateProject: (projectId, projectData) => apiClient.put(`/projects/${projectId}`, projectData),
  // 删除项目
  deleteProject: (projectId) => apiClient.delete(`/projects/${projectId}`),
};

// 聊天API
export const chatApi = {
  // 发送消息
  sendMessage: (messageData) => apiClient.post('/chat/messages', messageData),
  // 获取聊天历史
  getChatHistory: (projectId) => apiClient.get(`/chat/projects/${projectId}/history`),
  // 清空聊天历史
  clearChatHistory: (projectId) => apiClient.delete(`/chat/projects/${projectId}/history`),
};

// 知识库API
export const knowledgeApi = {
  // 添加知识库项目
  addKnowledgeItem: (itemData) => apiClient.post('/knowledge/items', itemData),
  // 获取项目的知识库
  getProjectKnowledge: (projectId) => apiClient.get(`/knowledge/projects/${projectId}/items`),
  // 获取知识库摘要
  getKnowledgeSummary: (projectId) => apiClient.get(`/knowledge/projects/${projectId}/summary`),
  // 检索知识库
  retrieveKnowledge: (requestData) => apiClient.post('/knowledge/retrieve', requestData),
  // 删除知识库项目
  deleteKnowledgeItem: (itemId) => apiClient.delete(`/knowledge/items/${itemId}`),
  // 生成每日学习总结
  generateDailySummary: (projectId) => apiClient.post(`/knowledge/projects/${projectId}/daily-summary`),
};

// 设置API
export const settingsApi = {
  // 获取应用设置
  getSettings: () => apiClient.get('/settings'),
  // 更新应用设置
  updateSettings: (settingsData) => apiClient.put('/settings', settingsData),
};

export default apiClient;
