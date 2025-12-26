# 📚 Supabase 题库数据库设置指南

## 第1步：创建 Supabase 项目

1. **登录 Supabase**
   - 访问：https://supabase.com/dashboard
   - 使用您的账号登录：lifanghe123@gmail.com

2. **创建新项目**
   - 点击 "New Project"
   - 填写信息：
     - **Name**: `math-problems-db`（或您喜欢的名称）
     - **Database Password**: 设置一个强密码（请记住！）
     - **Region**: 选择 `Singapore (ap-southeast-1)`（离国内最近）
     - **Pricing Plan**: Free（免费版足够）
   - 点击 "Create new project"
   - 等待 1-2 分钟（项目初始化）

## 第2步：获取连接信息

1. **进入项目设置**
   - 项目创建完成后，点击左侧菜单 "Settings" (⚙️)
   - 选择 "API"

2. **复制以下信息**：
   
   📋 **Project URL**（在 "Project URL" 部分）
   ```
   例如：https://xxxxxxxxxxxxx.supabase.co
   ```
   
   🔑 **API Key - anon public**（在 "Project API keys" 部分）
   ```
   例如：eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

## 第3步：创建数据库表

1. **打开 SQL Editor**
   - 点击左侧菜单 "SQL Editor"
   - 点击 "New query"

2. **复制并执行以下 SQL**：

```sql
-- 题目库表
CREATE TABLE problems (
  -- 基础信息
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- 题目内容
  problem_text TEXT NOT NULL,              -- 题目内容
  answer TEXT,                             -- 答案
  solution TEXT,                           -- 解析（解题过程）
  
  -- 分类信息
  teacher_name VARCHAR(255),               -- 出题老师
  category VARCHAR(255),                   -- 类别
  
  -- 对抗测试信息
  test_model VARCHAR(100),                 -- 对抗模型
  test_result JSONB,                       -- 对抗结果（JSON格式）
  test_accuracy DECIMAL(5,2),              -- 对抗正确率
  
  -- 质量和原创度信息
  quality_score JSONB,                     -- 质量评分
  originality_check JSONB,                 -- 原创度检测结果
  
  -- 元数据
  problem_hash TEXT,                       -- 题目哈希（用于快速查重）
  difficulty VARCHAR(50),                  -- 难度等级
  tags TEXT[],                            -- 标签数组
  
  -- 时间戳
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 创建索引（加速查询）
CREATE INDEX idx_problems_created ON problems(created_at DESC);
CREATE INDEX idx_problems_teacher ON problems(teacher_name);
CREATE INDEX idx_problems_category ON problems(category);
CREATE INDEX idx_problems_hash ON problems(problem_hash);
CREATE INDEX idx_problems_difficulty ON problems(difficulty);

-- 全文搜索索引
CREATE INDEX idx_problems_text_search ON problems 
  USING gin(to_tsvector('simple', problem_text));

-- 自动更新 updated_at 的触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_problems_updated_at BEFORE UPDATE
    ON problems FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

3. **点击 "Run" 执行 SQL**
   - 如果成功，会显示 "Success. No rows returned"

## 第4步：配置本地环境变量

1. **编辑 `.env` 文件**
   ```bash
   nano .env
   ```

2. **添加 Supabase 配置**（将 XXX 替换为您的实际值）：
   ```bash
   # Supabase Configuration
   SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

3. **保存并退出**

## 第5步：验证设置

在本地运行以下命令测试连接：

```bash
python test_supabase.py
```

如果看到 "✅ Supabase 连接成功！" 说明设置完成。

## ✅ 完成！

现在您可以：
- ✅ 添加题目到题库
- ✅ 查重检测
- ✅ 浏览和管理题库

---

## 🆘 常见问题

### 问题：忘记数据库密码
- 在 Supabase Dashboard → Settings → Database → 点击 "Reset database password"

### 问题：连接失败
- 检查 SUPABASE_URL 和 SUPABASE_KEY 是否正确
- 确认网络能访问 Supabase

### 问题：SQL 执行失败
- 检查是否有语法错误
- 确认表不存在（如果存在，先删除：`DROP TABLE IF EXISTS problems CASCADE;`）

