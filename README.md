# 数学题目审核系统

一个基于 GPT-5.1 的数学题目质量审核和原创度检测系统。

## 🌟 功能特点

- **📊 质量审核**：评估题目的清晰度、数学严谨性、完整性、可解性和教育价值
- **🔎 原创度检测**：检测题目是否存在相似题目，提供来源链接和相似度分析
- **🚀 实时分析**：使用 OpenAI GPT-5.1 进行智能分析
- **💾 结果下载**：支持下载 JSON 格式的审核报告

## 🛠️ 技术栈

- **前端框架**：Streamlit
- **AI 模型**：OpenAI GPT-5.1
- **部署**：Docker + Docker Compose
- **数据库**：Supabase（可选）

## 📦 本地开发

### 前置要求

- Python 3.11+
- OpenAI API Key

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/math-originality-checker.git
cd math-originality-checker
```

2. 创建虚拟环境
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env-example .env
# 编辑 .env 文件，填入你的 API Key
nano .env
```

5. 运行应用
```bash
streamlit run app.py
```

访问 http://localhost:8501

## 🐳 Docker 部署

### 使用 Docker Compose（推荐）

1. 配置环境变量
```bash
cp .env-example .env
# 编辑 .env 文件
nano .env
```

2. 启动服务
```bash
docker-compose up -d
```

3. 查看日志
```bash
docker-compose logs -f
```

4. 停止服务
```bash
docker-compose down
```

### 单独使用 Docker

```bash
# 构建镜像
docker build -t math-checker .

# 运行容器
docker run -d \
  -p 8501:8501 \
  -e OPENAI_API_KEY=your-key \
  --name math-checker \
  math-checker
```

## ☁️ 阿里云部署指南

### 服务器要求

- **推荐配置**：2核4G，5Mbps
- **推荐地域**：新加坡（可访问 OpenAI API，国内延迟低）
- **操作系统**：Ubuntu 22.04

### 部署步骤

1. **购买并配置服务器**
   - 登录阿里云控制台
   - 创建 ECS 实例（新加坡地域）
   - 安全组开放端口：22, 80, 443, 8501

2. **SSH 登录服务器**
```bash
ssh root@your-server-ip
```

3. **安装 Docker**
```bash
# 更新系统
apt update && apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装 Docker Compose
apt install docker-compose -y
```

4. **克隆代码**
```bash
git clone https://github.com/yourusername/math-originality-checker.git
cd math-originality-checker
```

5. **配置环境变量**
```bash
cp .env-example .env
nano .env
# 填入你的 OPENAI_API_KEY
```

6. **启动服务**
```bash
docker-compose up -d
```

7. **访问应用**
```
http://your-server-ip:8501
```

### 配置域名和 HTTPS（可选）

1. **安装 Nginx**
```bash
apt install nginx certbot python3-certbot-nginx -y
```

2. **配置 Nginx**
```bash
nano /etc/nginx/sites-available/math-checker
```

添加以下配置：
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

启用配置：
```bash
ln -s /etc/nginx/sites-available/math-checker /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

3. **配置 SSL 证书**
```bash
certbot --nginx -d yourdomain.com
```

## 🔧 环境变量

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | ✅ | - |
| `OPENAI_MODEL` | 使用的模型 | ❌ | gpt-5.1-chat-latest |
| `SUPABASE_URL` | Supabase 项目 URL | ❌ | - |
| `SUPABASE_KEY` | Supabase API Key | ❌ | - |

## 📊 集成 Supabase（可选）

如果需要保存审核历史和用户数据，可以集成 Supabase。

1. 在 Supabase 创建项目
2. 创建数据表（SQL）：

```sql
-- 审核记录表
CREATE TABLE problem_reviews (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  problem_text TEXT NOT NULL,
  review_type TEXT CHECK (review_type IN ('quality', 'originality')),
  result JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_reviews_created ON problem_reviews(created_at DESC);
CREATE INDEX idx_reviews_type ON problem_reviews(review_type);
```

3. 在 `.env` 中配置 Supabase 凭据
4. 取消 `docker-compose.yml` 中 Supabase 相关环境变量的注释

## 🔒 安全建议

- ✅ 不要将 `.env` 文件提交到 Git
- ✅ 定期更新依赖包
- ✅ 使用 HTTPS（生产环境）
- ✅ 配置防火墙规则
- ✅ 定期备份数据

## 📈 监控和维护

### 查看日志
```bash
docker-compose logs -f
```

### 重启服务
```bash
docker-compose restart
```

### 更新代码
```bash
git pull
docker-compose up -d --build
```

### 查看资源使用
```bash
docker stats
```

## 💰 成本估算

| 项目 | 费用 | 说明 |
|------|------|------|
| 阿里云 ECS（新加坡）| ¥200-300/月 | 2核4G，5Mbps |
| OpenAI API | 按使用计费 | GPT-5.1 约 $0.01/请求 |
| 域名 | ¥50-100/年 | 可选 |
| Supabase | 免费 | 免费版足够小规模使用 |

## 🐛 故障排查

### 问题：无法连接 OpenAI API
- 检查服务器是否能访问 OpenAI（香港服务器不行）
- 确认 API Key 是否正确配置
- 查看服务日志：`docker-compose logs`

### 问题：端口被占用
```bash
# 查看端口占用
netstat -tulpn | grep 8501
# 修改 docker-compose.yml 中的端口映射
```

### 问题：内存不足
- 升级服务器配置
- 或减少并发请求

## 📝 License

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请通过 GitHub Issues 联系。

---

⭐ 如果这个项目对你有帮助，请给个 Star！

