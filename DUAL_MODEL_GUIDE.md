# 🤖 双模型原创度检测指南

## 功能说明

使用 **GPT-5.1** 和 **DeepSeek V3** 两个大模型交叉验证题目原创性，提高检测准确度。

### 优势

1. ✅ **交叉验证** - 两个模型独立分析，结果更可靠
2. ✅ **对比分析** - 显示两个模型的结论差异
3. ✅ **高可信度** - 结论一致时可信度更高
4. ✅ **人工辅助** - 结论不同时提供详细分析供人工判断

---

## 第1步：获取 DeepSeek API Key

### 1.1 注册 DeepSeek 账号

访问：https://platform.deepseek.com/

- 点击右上角"登录/注册"
- 可以用邮箱或第三方账号注册
- 新用户有免费额度

### 1.2 创建 API Key

1. 登录后进入控制台
2. 点击左侧菜单 "API Keys"
3. 点击"创建新密钥"
4. 复制生成的 API Key（格式类似：`sk-xxxxx`）
5. **重要**：妥善保存，离开页面后无法再次查看

### 1.3 费用说明

```
DeepSeek V3 定价：
- 输入: ¥1.0 / 1M tokens
- 输出: ¥2.0 / 1M tokens

新用户：免费 ¥10 额度
```

---

## 第2步：本地测试（可选）

### 2.1 更新本地代码

```bash
cd /Users/fangheli/math-originality-checker

# 备份原文件
cp app.py app_single_model.py

# 使用双模型版本
cp app_dual_model.py app.py
```

### 2.2 配置环境变量

编辑 `.env` 文件：

```bash
# OpenAI API Key（必需）
OPENAI_API_KEY=sk-proj-你的OpenAI-Key

# DeepSeek API Key（必需 - 用于双模型对比）
DEEPSEEK_API_KEY=sk-你的DeepSeek-Key

# 模型配置
OPENAI_MODEL=gpt-5.1-chat-latest
```

### 2.3 本地测试

```bash
# 重启本地应用
source .venv/bin/activate
streamlit run app.py
```

访问 http://localhost:8501 测试功能

---

## 第3步：部署到阿里云

### 方法A：自动部署（推荐）

#### 3.1 提交代码到 GitHub

```bash
cd /Users/fangheli/math-originality-checker

# 备份并替换主文件
git add .
git commit -m "Add dual model support for originality detection"
git push
```

#### 3.2 更新服务器

SSH 登录服务器后执行：

```bash
cd math-originality-checker

# 拉取最新代码
git pull

# 更新环境变量
nano .env
# 添加一行：
# DEEPSEEK_API_KEY=sk-你的DeepSeek-Key

# 备份单模型版本
cp app.py app_single_model.py

# 使用双模型版本
cp app_dual_model.py app.py

# 重启服务
docker-compose restart

# 查看日志确认启动成功
docker-compose logs -f
```

---

### 方法B：手动部署

如果代码还没提交到 GitHub：

#### 3.1 在服务器上直接创建文件

SSH 登录服务器，创建新文件：

```bash
cd /root/math-originality-checker
nano app_dual_model.py
```

粘贴双模型代码，保存退出。

#### 3.2 更新配置

```bash
# 配置 DeepSeek API Key
nano .env
# 添加：DEEPSEEK_API_KEY=sk-你的Key

# 切换到双模型版本
mv app.py app_single_model.py
mv app_dual_model.py app.py

# 重启
docker-compose restart
```

---

## 第4步：测试双模型功能

### 4.1 访问应用

```
http://47.236.135.225:8501
```

### 4.2 测试步骤

1. 输入一个数学题目
2. 点击 **"🔎 原创度检测（双模型）"**
3. 等待两个模型分析（约 10-20 秒）
4. 查看 **"对比总结"** 标签页：
   - 如果两个模型结论一致 → ✅ 高可信度
   - 如果结论不同 → ⚠️ 查看各自的详细分析

### 4.3 结果解读

**场景 1：结论一致**
```
GPT-5.1:     原创
DeepSeek V3: 原创
→ ✅ 高可信度，题目很可能是原创
```

**场景 2：结论不同**
```
GPT-5.1:     疑似搬运
DeepSeek V3: 结构雷同
→ ⚠️ 需要查看详细分析
→ 检查相似题目来源是否真实
→ 人工判断最终结论
```

**场景 3：一个发现相似，一个未发现**
```
GPT-5.1:     原创（未发现相似）
DeepSeek V3: 疑似搬运（发现2个相似题目）
→ ⚠️ 重点关注 DeepSeek 发现的相似题目
→ 验证来源链接
→ 判断是否真的相似
```

---

## 使用建议

### 💡 最佳实践

1. **优先看对比结论**
   - 结论一致 → 可信度高，直接采用
   - 结论不同 → 深入分析差异

2. **验证来源链接**
   - 点击提供的链接查看原题
   - 确认相似度是否准确

3. **综合判断**
   - 参考两个模型的关键词分析
   - 比较结构分析的差异
   - 结合实际情况做最终判断

4. **保存结果**
   - 下载 JSON 报告
   - 记录重要发现

### ⚙️ 性能优化

- 单个题目检测约需 10-20 秒
- 成本约 ¥0.02-0.05 / 题
- 批量检测时可以考虑并行处理

### 🔒 安全提示

- 不要将 API Key 提交到 Git
- 定期更换 API Key
- 监控 API 使用量

---

## 故障排查

### 问题1：DeepSeek 调用失败

**检查**：
```bash
# 查看日志
docker-compose logs

# 确认环境变量
cat .env | grep DEEPSEEK
```

**解决**：
- 确认 API Key 正确
- 检查余额是否充足
- 验证网络连接

### 问题2：只显示单模型结果

**原因**：未配置 DeepSeek API Key

**解决**：
1. 在 `.env` 中添加 `DEEPSEEK_API_KEY`
2. 重启服务：`docker-compose restart`

### 问题3：结果加载慢

**原因**：两个 API 串行调用

**优化**：
- 已经使用异步加载
- 正常需要 10-20 秒
- 如果超过 30 秒，检查网络

---

## 回退到单模型

如果不想使用双模型，可以回退：

```bash
cd /root/math-originality-checker
mv app.py app_dual_model_backup.py
mv app_single_model.py app.py
docker-compose restart
```

---

## 成本估算

```
假设每天检测 100 道题：

OpenAI GPT-5.1:
  100 题 × $0.01 = $1.00 / 天

DeepSeek V3:
  100 题 × ¥0.03 = ¥3.00 / 天

总计：约 $1.50 / 天 = $45 / 月
```

相比单模型增加约 30% 成本，但准确度显著提升！

---

需要帮助？检查日志：
```bash
docker-compose logs -f
```

