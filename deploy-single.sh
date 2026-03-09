#!/bin/bash

set -e

echo "=========================================="
echo "  AI Learning Assistant 单一容器部署脚本"
echo "=========================================="

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "错误: Docker 未安装"
        echo "请先安装 Docker: https://docs.docker.com/engine/install/centos/"
        exit 1
    fi

    if ! command -v docker &> /dev/null; then
        echo "错误: Docker Compose 未安装"
        exit 1
    fi

    echo "Docker 已安装"
}

check_env() {
    if [ ! -f .env ]; then
        echo "错误: .env 文件不存在"
        echo "请复制 .env.example 并填入你的 API 密钥:"
        echo "  cp .env.example .env"
        echo "  nano .env"
        exit 1
    fi
    echo ".env 文件存在"
}

check_ports() {
    echo "检查端口占用..."
    
    if netstat -tlnp 2>/dev/null | grep -q ":80 "; then
        echo "警告: 端口 80 已被占用"
        echo "请修改 docker-compose-single.yml 中的前端端口映射"
    else
        echo "端口 80 可用"
    fi

    if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
        echo "警告: 端口 8000 已被占用"
        echo "请修改 docker-compose-single.yml 中的后端端口映射"
    else
        echo "端口 8000 可用"
    fi
}

deploy() {
    echo ""
    echo "开始构建和启动单一容器..."
    
    docker compose -f docker-compose-single.yml down 2>/dev/null || true
    
    docker compose -f docker-compose-single.yml build --no-cache
    
    docker compose -f docker-compose-single.yml up -d
    
    echo ""
    echo "=========================================="
    echo "  部署完成!"
    echo "=========================================="
    echo ""
    echo "前端访问地址: http://$(hostname -I | awk '{print $1}')"
    echo "后端 API 地址: http://$(hostname -I | awk '{print $1}'):8000"
    echo "API 文档地址: http://$(hostname -I | awk '{print $1}'):8000/docs"
    echo ""
    echo "常用命令:"
    echo "  查看日志: docker compose -f docker-compose-single.yml logs -f"
    echo "  停止服务: docker compose -f docker-compose-single.yml down"
    echo "  重启服务: docker compose -f docker-compose-single.yml restart"
    echo ""
}

main() {
    check_docker
    check_env
    check_ports
    deploy
}

main "$@"
