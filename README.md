# AI学习助手 (MVP版)

## 项目概述

构建一个基于多智能体协作的AI学习助手，帮助用户以项目制方式学习任何主题。核心特色：每个项目拥有一个AI智能体团队，自动生成每日学习笔记与知识库，实现个性化、持续性的学习体验。

## 核心功能模块

### 1. 项目管理模块
- 创建项目：用户输入主题（如"量子物理入门"），AI自动生成项目结构（智能体角色、学习路径）。
- 项目仪表盘：展示项目进度、知识点掌握情况、待复习点、知识图谱（简易版用列表展示）。

### 2. 多智能体协作模块
- 预定义智能体角色：
  - @理论导师：解释概念、原理。
  - @实践教练：提供代码/实验步骤。
  - @提问者：提出启发式问题。
- 用户可在对话中 @ 任一智能体提问。
- 智能体之间能协作：例如@理论导师解释原理后，@实践教练自动提供代码示例。

### 3. 动态知识库模块
- 每日总结：用户点击"结束今日学习"后，AI自动生成：
  - 精简笔记（核心概念、代码片段）
  - 疑惑点标记（用户反复提问处）
  - 兴趣点标记（用户追问较多处）
- 知识检索：次日学习时，AI可引用昨日知识库；用户可随时查询历史内容（如"昨天关于决策树的代码？"）。

### 4. 用户界面
- 对话式主界面：类似Slack频道，每个项目一个工作区，显示所有智能体消息。
- 知识库视图：独立页面，展示所有笔记，支持Markdown编辑和搜索。
- 简易可视化：进度条（基于对话轮次/知识点数量）。

## 技术栈

### 前端
- React + Tailwind CSS (使用Vite构建)
- Material UI (MUI) 组件库
- Axios (API调用)
- React Markdown (Markdown渲染)

### 后端
- Python FastAPI
- LangChain + OpenAI API (GPT-4或GPT-3.5)
- Chroma (向量数据库)
- Pydantic (数据验证)
- python-dotenv (环境变量管理)

## 项目结构

```
ai-learning-assistant/
├── backend/              # 后端代码
│   ├── agents/           # 智能体相关代码
│   │   ├── agent_team.py           # 智能体团队实现
│   │   ├── agent_manager.py        # 智能体管理
│   │   └── project_initializer.py  # 项目初始化
│   ├── knowledge_base/   # 知识库相关代码
│   │   └── daily_summary.py        # 每日总结服务
│   ├── models/           # 数据模型
│   │   ├── project.py              # 项目模型
│   │   ├── chat.py                 # 聊天模型
│   │   └── knowledge.py            # 知识库模型
│   ├── routes/           # API路由
│   │   ├── project.py              # 项目管理路由
│   │   ├── chat.py                 # 聊天路由
│   │   ├── knowledge.py            # 知识库路由
│   │   └── settings.py             # 设置路由
│   ├── services/         # 业务逻辑
│   │   └── settings_service.py     # 设置服务
│   ├── vector_db/        # 向量数据库
│   │   └── vector_db_manager.py    # 向量数据库管理
│   ├── .env              # 环境变量配置
│   ├── main.py           # 后端入口
│   └── requirements.txt  # 依赖包
├── frontend/             # 前端代码
│   ├── public/           # 静态资源
│   ├── src/              # 源代码
│   │   ├── components/   # 组件
│   │   │   ├── ChatInterface/      # 聊天界面组件
│   │   │   ├── KnowledgeBase/      # 知识库组件
│   │   │   ├── ProjectManager/     # 项目管理组件
│   │   │   └── Settings/           # 设置组件
│   │   ├── services/     # 服务
│   │   │   └── api.js              # API调用服务
│   │   ├── App.jsx       # 应用主组件
│   │   └── main.jsx      # 前端入口
│   ├── .gitignore        # Git忽略文件
│   ├── package.json      # 前端依赖
│   └── vite.config.js    # Vite配置
└── README.md             # 项目文档
```

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- OpenAI API Key

### 后端安装
1. 进入后端目录
   ```bash
   cd backend
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量
   编辑 `.env` 文件，填入你的API密钥：
   ```
   # API Keys
   GOOGLE_API_KEY=your-google-api-key
   OPENAI_API_KEY=your-openai-api-key
   
   # FastAPI Settings
   FASTAPI_HOST=0.0.0.0
   FASTAPI_PORT=8000
   
   # Vector Database Settings
   VECTOR_DB_PATH=../vector_db
   CHROMA_DB_PATH=./vector_db
   
   # OpenAI Settings
   OPENAI_MODEL=gpt-3.5-turbo
   ```

4. 启动后端服务
   ```bash
   uvicorn main:app --reload
   ```
   后端服务将在 http://localhost:8000 运行

### 前端安装
1. 进入前端目录
   ```bash
   cd frontend
   ```

2. 安装依赖
   ```bash
   npm install
   ```

3. 启动前端服务
   ```bash
   npm run dev
   ```
   前端服务将在 http://localhost:5173 运行

## 使用指南

### 1. 创建学习项目
1. 在前端界面点击"创建项目"
2. 输入项目名称、学习主题和描述
3. 点击"创建"按钮，系统会自动生成项目结构和推荐的智能体

### 2. 与智能体对话
1. 选择一个项目进入聊天界面
2. 在输入框中输入问题，或点击智能体标签快速@智能体
3. 点击发送按钮，智能体会根据问题类型提供专业回答
4. 可以同时@多个智能体获取不同角度的回答

### 3. 生成每日学习总结
1. 在聊天界面点击"每日总结"按钮
2. 系统会分析当日的对话历史，生成学习总结
3. 总结会自动保存到知识库中

### 4. 管理知识库
1. 进入知识库界面，查看所有学习笔记
2. 使用搜索功能查找特定知识点
3. 可以手动添加、编辑或删除知识点
4. 知识库会按类型（概念、笔记、疑惑点、兴趣点）分类显示

### 5. 系统设置
1. 进入设置界面，配置API密钥和模型参数
2. 可以调整模型温度、最大令牌数等参数
3. 保存设置后，新的配置会立即生效

## API文档

后端服务启动后，可以访问 http://localhost:8000/docs 查看详细的API文档。

## 项目亮点

1. **多智能体协作**：不同角色的智能体协同工作，提供全面的学习支持
2. **动态知识库**：自动生成和更新学习笔记，形成个性化知识体系
3. **检索增强生成**：利用向量数据库检索相关知识，提高回答的准确性和相关性
4. **用户友好界面**：直观的对话式界面，支持Markdown渲染和智能体@提及
5. **灵活可扩展**：模块化设计，易于添加新的智能体角色和功能

## 未来规划

1. **更多智能体角色**：添加领域专家、学习顾问等角色
2. **知识图谱可视化**：实现更直观的知识关系展示
3. **学习进度跟踪**：更详细的学习数据分析和建议
4. **多语言支持**：支持中文、英文等多种语言
5. **移动端适配**：开发移动应用，实现随时随地学习

## 贡献指南

欢迎提交Issue和Pull Request，共同改进这个项目。

## 许可证

MIT License
