FROM python:3.10-slim as backend-build

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

FROM node:18-alpine as frontend-build

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制后端
COPY --from=backend-build /app/backend /app/backend
# 复制前端构建产物
COPY --from=frontend-build /app/frontend/dist /var/www/html

# 复制 Nginx 配置
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# 安装后端依赖（如果需要）
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# 环境变量
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV BASE_URL=${BASE_URL}
ENV MODEL_NAME=${MODEL_NAME}
ENV FASTAPI_HOST=0.0.0.0
ENV FASTAPI_PORT=8000
ENV VECTOR_DB_PATH=/app/backend/vector_db
ENV CHROMA_DB_PATH=/app/backend/vector_db

# 端口
EXPOSE 80
EXPOSE 8000

# 创建启动脚本
RUN bash -c 'cat > /app/start.sh << "EOF"
#!/bin/bash

# 启动 Nginx
nginx

# 启动后端
cd /app/backend
uvicorn main:app --host 0.0.0.0 --port 8000
EOF'

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
