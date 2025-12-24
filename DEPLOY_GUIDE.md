# 📦 部署指南

完整的步骤指导，从代码上传到应用上线。

## 第一步：准备 GitHub 仓库

### 1.1 在 GitHub 创建新仓库

1. 访问 https://github.com/new
2. 填写信息：
   - Repository name: `math-originality-checker`
   - Description: `数学题目质量审核和原创度检测系统`
   - 选择 Public 或 Private
   - ⚠️ **不要**勾选 "Add a README file"（我们已经有了）
3. 点击 "Create repository"

### 1.2 上传代码到 GitHub

在本地项目目录执行：

```bash
# 初始化 Git（如果还没有）
git init

# 添加所有文件
git add .

# 查看将要提交的文件
git status

# 创建首次提交
git commit -m "Initial commit: Math originality checker with quality review"

# 关联远程仓库（替换 yourusername）
git remote add origin https://github.com/yourusername/math-originality-checker.git

# 推送代码
git push -u origin main
```

⚠️ **重要**：确保你的 `.env` 文件已被 `.gitignore` 忽略，不会被上传！

---

## 第二步：配置 Supabase（可选）

如果需要保存审核历史记录：

### 2.1 创建 Supabase 项目

1. 访问 https://supabase.com
2. 点击 "New Project"
3. 填写项目信息：
   - Name: `math-checker`
   - Database Password: 设置一个强密码
   - Region: 选择 `Singapore`（推荐）
4. 等待项目创建（约 2 分钟）

### 2.2 创建数据表

1. 在 Supabase 控制台，点击左侧 "SQL Editor"
2. 点击 "New Query"
3. 复制 `supabase-schema.sql` 的内容
4. 粘贴并点击 "Run" 执行

### 2.3 获取 API 凭据

1. 点击左侧 "Settings" → "API"
2. 复制以下信息：
   - `Project URL` (例如: https://xxx.supabase.co)
   - `anon/public key`（API Key）

---

## 第三步：购买阿里云服务器

### 3.1 选择配置

1. 登录阿里云控制台
2. 进入 "云服务器 ECS"
3. 点击 "创建实例"

**推荐配置**：
```
地域：新加坡
实例规格：ecs.t6-c1m2.large（2核4G）
镜像：Ubuntu 22.04 64位
网络：按流量计费，5Mbps
系统盘：40GB 高效云盘
购买时长：1个月（测试）或更长
```

### 3.2 配置安全组

在创建实例时或创建后配置：

| 规则方向 | 协议 | 端口范围 | 授权对象 | 说明 |
|---------|------|---------|---------|------|
| 入方向 | TCP | 22 | 0.0.0.0/0 | SSH 登录 |
| 入方向 | TCP | 80 | 0.0.0.0/0 | HTTP |
| 入方向 | TCP | 443 | 0.0.0.0/0 | HTTPS |
| 入方向 | TCP | 8501 | 0.0.0.0/0 | Streamlit |

### 3.3 设置 root 密码

创建实例后，如果没有设置密码：
1. 在实例列表找到你的实例
2. 点击 "更多" → "重置实例密码"
3. 设置密码并重启实例

---

## 第四步：部署到阿里云

### 4.1 连接服务器

```bash
# 使用 SSH 连接（替换为你的服务器 IP）
ssh root@your-server-ip

# 首次连接会询问是否信任，输入 yes
# 然后输入密码
```

### 4.2 方法 A：使用自动部署脚本（推荐）

```bash
# 下载部署脚本
wget https://raw.githubusercontent.com/yourusername/math-originality-checker/main/deploy-aliyun.sh

# 运行部署脚本
bash deploy-aliyun.sh
```

脚本会自动：
- 安装 Docker 和 Docker Compose
- 克隆代码
- 配置环境变量
- 启动服务

### 4.2 方法 B：手动部署

#### 4.2.1 安装 Docker

```bash
# 更新系统
apt update && apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装 Docker Compose
apt install docker-compose -y

# 验证安装
docker --version
docker-compose --version
```

#### 4.2.2 克隆代码

```bash
# 安装 Git
apt install git -y

# 克隆仓库（替换为你的仓库地址）
git clone https://github.com/yourusername/math-originality-checker.git
cd math-originality-checker
```

#### 4.2.3 配置环境变量

```bash
# 复制环境变量模板
cp .env-example .env

# 编辑环境变量
nano .env
```

填入以下信息：
```env
# OpenAI API Key（必需）
OPENAI_API_KEY=sk-proj-你的API-Key

# 模型名称（可选）
OPENAI_MODEL=gpt-5.1-chat-latest

# Supabase（可选，如果不用可以不填）
# SUPABASE_URL=https://xxx.supabase.co
# SUPABASE_KEY=你的Supabase-Key
```

保存文件：`Ctrl + X` → `Y` → `Enter`

#### 4.2.4 启动服务

```bash
# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志（确认启动成功）
docker-compose logs -f
```

看到类似信息说明启动成功：
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://172.x.x.x:8501
```

按 `Ctrl + C` 退出日志查看。

---

## 第五步：访问应用

### 5.1 获取服务器 IP

在阿里云控制台查看，或在服务器执行：
```bash
curl ifconfig.me
```

### 5.2 访问应用

在浏览器打开：
```
http://your-server-ip:8501
```

🎉 如果看到应用界面，说明部署成功！

---

## 第六步：配置域名和 HTTPS（可选）

### 6.1 准备域名

1. 购买域名（如果还没有）
2. 在域名管理控制台添加 A 记录：
   ```
   记录类型：A
   主机记录：@ 或 www
   记录值：your-server-ip
   TTL：10分钟
   ```
3. 等待 DNS 生效（5-30分钟）

### 6.2 安装 Nginx

```bash
apt install nginx certbot python3-certbot-nginx -y
```

### 6.3 配置 Nginx

```bash
# 创建配置文件
nano /etc/nginx/sites-available/math-checker
```

粘贴以下内容（替换 yourdomain.com）：

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

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

保存并启用配置：

```bash
# 创建软链接
ln -s /etc/nginx/sites-available/math-checker /etc/nginx/sites-enabled/

# 测试配置
nginx -t

# 重启 Nginx
systemctl restart nginx
```

### 6.4 配置 SSL 证书（HTTPS）

```bash
# 使用 Let's Encrypt 免费证书
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 按提示操作：
# 1. 输入邮箱
# 2. 同意服务条款
# 3. 选择是否重定向 HTTP 到 HTTPS（推荐选择 2）
```

证书配置成功后，你的应用就可以通过 HTTPS 访问了：
```
https://yourdomain.com
```

### 6.5 设置自动续期

Let's Encrypt 证书有效期 90 天，需要定期续期：

```bash
# 测试自动续期
certbot renew --dry-run

# 如果成功，cron 会自动续期，无需手动操作
```

---

## 常用运维命令

### 查看状态
```bash
docker-compose ps
docker-compose logs -f
docker stats
```

### 重启服务
```bash
docker-compose restart
```

### 更新代码
```bash
cd math-originality-checker
git pull
docker-compose up -d --build
```

### 停止服务
```bash
docker-compose down
```

### 查看系统资源
```bash
# 内存使用
free -h

# 磁盘使用
df -h

# CPU 和进程
htop
```

---

## 故障排查

### 问题 1：无法访问应用

**检查服务是否运行**：
```bash
docker-compose ps
# 应该看到 State 为 Up
```

**检查端口是否监听**：
```bash
netstat -tulpn | grep 8501
```

**检查防火墙**：
```bash
# 如果有 ufw
ufw status
ufw allow 8501
```

### 问题 2：API 调用失败

**检查环境变量**：
```bash
cat .env
# 确认 OPENAI_API_KEY 是否正确
```

**测试 OpenAI 连接**：
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer your-api-key"
```

### 问题 3：内存不足

**查看内存使用**：
```bash
free -h
docker stats
```

**重启服务释放内存**：
```bash
docker-compose restart
```

或升级服务器配置。

### 问题 4：端口冲突

修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8502:8501"  # 使用 8502 端口
```

---

## 安全建议

1. ✅ 修改 SSH 端口（默认 22）
2. ✅ 禁用 root 密码登录，使用 SSH 密钥
3. ✅ 安装 fail2ban 防止暴力破解
4. ✅ 定期更新系统和软件包
5. ✅ 配置防火墙规则
6. ✅ 定期备份数据

---

## 成本优化

1. 使用按量付费，根据使用情况调整配置
2. 设置费用预警
3. 监控 API 调用次数
4. 考虑使用 CDN 加速（如果有域名）

---

🎉 **恭喜！你已经完成了完整的部署流程！**

如有问题，请查看日志或提交 GitHub Issue。

