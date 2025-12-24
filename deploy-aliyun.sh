#!/bin/bash
# 阿里云服务器快速部署脚本
# 使用方法：在服务器上运行 bash deploy-aliyun.sh

set -e

echo "========================================"
echo "数学题目审核系统 - 阿里云部署脚本"
echo "========================================"
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 root 权限运行此脚本"
    echo "运行: sudo bash deploy-aliyun.sh"
    exit 1
fi

echo "📦 步骤 1/6: 更新系统..."
apt update && apt upgrade -y

echo ""
echo "🐳 步骤 2/6: 安装 Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "✅ Docker 安装完成"
else
    echo "✅ Docker 已安装"
fi

echo ""
echo "🔧 步骤 3/6: 安装 Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    apt install docker-compose -y
    echo "✅ Docker Compose 安装完成"
else
    echo "✅ Docker Compose 已安装"
fi

echo ""
echo "📁 步骤 4/6: 克隆代码..."
if [ ! -d "math-originality-checker" ]; then
    read -p "请输入 GitHub 仓库地址: " REPO_URL
    git clone "$REPO_URL" math-originality-checker
    cd math-originality-checker
else
    echo "⚠️  目录已存在，跳过克隆"
    cd math-originality-checker
    git pull
fi

echo ""
echo "🔑 步骤 5/6: 配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env-example .env
    echo "⚠️  请编辑 .env 文件，填入你的 OPENAI_API_KEY"
    echo ""
    read -p "请输入你的 OpenAI API Key: " API_KEY
    sed -i "s/your-openai-api-key-here/$API_KEY/" .env
    echo "✅ 环境变量配置完成"
else
    echo "✅ .env 文件已存在"
fi

echo ""
echo "🚀 步骤 6/6: 启动服务..."
docker-compose up -d

echo ""
echo "========================================"
echo "✅ 部署完成！"
echo "========================================"
echo ""
echo "📊 服务状态:"
docker-compose ps
echo ""
echo "🌐 访问地址:"
SERVER_IP=$(curl -s ifconfig.me)
echo "   http://$SERVER_IP:8501"
echo ""
echo "📝 常用命令:"
echo "   查看日志: docker-compose logs -f"
echo "   重启服务: docker-compose restart"
echo "   停止服务: docker-compose down"
echo "   更新代码: git pull && docker-compose up -d --build"
echo ""
echo "🎉 部署成功！请访问上面的地址测试应用。"

