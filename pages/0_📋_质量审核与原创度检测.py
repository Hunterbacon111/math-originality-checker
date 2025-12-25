#!/usr/bin/env python3
"""
数学题目质量审核与原创度检测系统 - 图片识别版
支持文字输入和图片上传（OCR识别）
"""
import streamlit as st
import json
import time
import os
import base64
from openai import OpenAI
from PIL import Image
import io
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="质量审核与原创度检测",
    page_icon="📋",
    layout="wide"
)

# API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.1-chat-latest")
MISTRAL_VISION_MODEL = "pixtral-large-latest"  # Mistral 的视觉模型
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# 检查配置
if not OPENAI_API_KEY:
    st.error("❌ 未配置 OPENAI_API_KEY")
    st.stop()

if not MISTRAL_API_KEY:
    st.error("❌ 未配置 MISTRAL_API_KEY（图像识别需要）")
    st.stop()

if not DEEPSEEK_API_KEY:
    st.warning("⚠️ 未配置 DEEPSEEK_API_KEY，将只使用 GPT-5.1")
    DUAL_MODEL_ENABLED = False
else:
    DUAL_MODEL_ENABLED = True

# 质量审核 Prompt
REVIEW_PROMPT_TEMPLATE = """You are an expert mathematics educator reviewing problem quality.

**IMPORTANT**: Do NOT attempt to solve the problem or verify if the answer is correct. Focus ONLY on evaluating the problem statement itself.

Evaluate this mathematical problem based on these 5 criteria:
1. **Clarity** (0-2 points): Is the problem statement clear, unambiguous, and easy to understand?
2. **Mathematical Rigor** (0-2 points): Are mathematical notations, symbols, and expressions used correctly and rigorously?
3. **Completeness** (0-2 points): Does the problem provide all necessary information? Are conditions sufficient to solve it?
4. **Solvability** (0-2 points): Does the problem appear to have a well-defined solution (unique or a clear solution set)?
5. **Educational Value** (0-2 points): Is this a meaningful mathematical problem worth studying?

**Problem to Review:**
{problem_text}

**Your Task:**
Evaluate the problem based on the 5 criteria above and respond in JSON format:

{{
  "clarity_score": 0-2,
  "rigor_score": 0-2,
  "completeness_score": 0-2,
  "solvability_score": 0-2,
  "educational_value_score": 0-2,
  "total_score": 0-10,
  "issues": ["list specific issues, if any"],
  "reasoning": "brief explanation of your evaluation",
  "recommendation": "ACCEPT (≥7) / BORDERLINE (5-6) / REJECT (<5)"
}}

**Remember**: Focus on problem quality, NOT answer correctness!
"""

# 原创度检测 Prompt - GPT-5.1 版本
ORIGINALITY_PROMPT_GPT = """你现在是一名资深的学术查重专家和高级搜索工程专家。

Task: 请针对我提供的题目进行深度分析，查验该题目的原创度（是否在你的知识库中存在原题或高度相似的变体）。

**重要说明**：
- 严禁给出任何解题步骤或答案
- 不要尝试解题
- 只分析题目本身的原创性

**检索策略 (Search Strategy)**:
1. 关键词抽样：提取题目的核心知识点、罕见术语和数据组合
2. 结构化匹配：忽略具体的数值，重点关注题目的逻辑结构、设定背景和已知条件的组合方式
3. 多平台覆盖：在你的知识库中检索包括但不限于：
   - 经典教材（如同济高等数学、普林斯顿微积分等）
   - 标准题库（高考真题、考研真题、AMC、IMO 等）
   - 知名教育平台和论坛（AOPS、知乎、百度教育、StackExchange、Chegg 等）
   - 学术论文和竞赛题库

**分析要求 (Analysis Requirements)**:
- 不仅要看语义和数字，还要关注解题路径的相似性
- **如果发现相似题目，必须提供具体来源信息**：
  - 如果来自网站/论坛，提供完整的URL链接
  - 如果来自书籍/试卷，提供详细出处
  - 如果来自竞赛，提供年份和题号
- 分析题目的独特之处

**题目内容**:
{problem_text}

**输出格式 (Output Format)**:
请以 JSON 格式输出，包含以下字段：

{{
  "originality_conclusion": "原创 / 疑似搬运 / 结构雷同",
  "similar_problems": [
    {{
      "source": "来源名称",
      "source_url": "具体链接或详细出处",
      "content": "相似题目的简要描述",
      "similarity_percentage": 85,
      "similarity_reason": "相似之处的具体说明"
    }}
  ],
  "unique_aspects": ["列出题目的独特之处"],
  "keyword_analysis": "关键词和核心概念分析",
  "structure_analysis": "题目结构和逻辑框架分析",
  "overall_assessment": "整体评估说明"
}}

**重要提醒**: 
1. 必须提供具体的来源链接或详细出处
2. 不要给原创度打分
3. 严禁在任何字段中包含解题步骤或答案！
"""

# 原创度检测 Prompt - DeepSeek R1 版本（强调准确性）
ORIGINALITY_PROMPT_DEEPSEEK = """你是一名严谨的学术查重专家。你的任务是分析题目的原创度。

⚠️ **极其重要的警告**：
1. **绝对禁止编造或臆测来源信息**
2. **只有在100%确定的情况下才能说"找到相似题目"**
3. **不确定时，必须明确说"未找到相似题目"或"原创"**
4. **提供的链接必须是你确切知道存在的，不要编造URL**
5. **宁可保守也不要给出虚假信息**

Task: 在你的知识库中检索是否存在与以下题目相似的内容。

**题目内容**:
{problem_text}

**严格检索要求**:
1. 只检索你训练数据中**确实存在**的相似题目
2. 如果不确定或没有找到，直接返回"原创"结论
3. 不要基于推测或想象提供来源
4. 链接必须是真实存在的（如果不确定链接是否存在，就不要提供）

**输出格式**:
{{
  "originality_conclusion": "原创 / 疑似搬运 / 结构雷同",
  "similar_problems": [
    {{
      "source": "来源名称（必须确切知道）",
      "source_url": "具体链接或详细出处（如果不确定链接，写'出处待确认'）",
      "content": "相似题目的简要描述",
      "similarity_percentage": 85,
      "similarity_reason": "相似之处的具体说明",
      "confidence_level": "高/中/低（你对此来源真实性的信心）"
    }}
  ],
  "unique_aspects": ["列出题目的独特之处"],
  "keyword_analysis": "关键词分析",
  "structure_analysis": "题目结构分析",
  "overall_assessment": "整体评估",
  "search_note": "说明你的检索过程和结果可靠性"
}}

**再次强调**：
- ❌ 不要编造 artofproblemsolving.com、zhihu.com 等网站的具体链接
- ❌ 不要编造书籍页码和例题编号
- ✅ 只有真正在训练数据中见过的才能列出
- ✅ 不确定的情况下，诚实地说"原创"或"无法确定"

**严禁给出解题步骤或答案！**
"""

def encode_image_to_base64(image_file):
    """将上传的图片转换为 base64"""
    image = Image.open(image_file)
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def extract_text_from_image(image_file):
    """使用 Mistral Pixtral 从图片中提取数学题目"""
    try:
        # 使用 Mistral API（兼容 OpenAI SDK）
        client = OpenAI(
            api_key=MISTRAL_API_KEY,
            base_url="https://api.mistral.ai/v1"
        )
        
        # 将图片转换为 base64
        base64_image = encode_image_to_base64(image_file)
        
        response = client.chat.completions.create(
            model=MISTRAL_VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """You are an expert OCR system for mathematical content. Please carefully extract ALL text from this image.

CRITICAL REQUIREMENTS:
1. Extract ALL visible text, formulas, and mathematical symbols
2. Preserve the exact structure and formatting
3. Use proper mathematical notation (e.g., ∠ABC, °, √, ∫, etc.)
4. If there are diagrams, describe them briefly
5. Include ALL text - do NOT refuse or skip any content
6. Output ONLY the extracted text, no explanations

Extract the complete mathematical problem from the image:"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        extracted = response.choices[0].message.content.strip()
        
        # 检查返回内容
        if not extracted or len(extracted) < 10:
            return "❌ 识别失败：返回内容过短，请重新上传图片或使用文字输入"
        
        # 检查是否拒绝识别
        refusal_keywords = ["sorry", "can't", "cannot", "unable", "refuse"]
        if any(keyword in extracted.lower() for keyword in refusal_keywords):
            return f"❌ Mistral 拒绝识别此图片\n\n返回内容: {extracted}\n\n💡 请使用文字输入功能"
        
        return extracted
    
    except Exception as e:
        return f"""❌ 图片识别失败: {str(e)}

💡 可能的原因：
1. Mistral API Key 配置错误
2. 网络连接问题
3. 图片格式不支持

🔧 解决方案：
1. 使用 **文字输入** 功能手动输入题目
2. 检查 Mistral API Key 是否正确
3. 尝试重新上传更清晰的图片"""

def call_openai_api(prompt, api_key, model, base_url="https://api.openai.com/v1"):
    """调用 API（支持 OpenAI 和 DeepSeek）"""
    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}

def get_recommendation_emoji(recommendation):
    """根据推荐结果返回表情符号"""
    if "ACCEPT" in recommendation:
        return "✅"
    elif "BORDERLINE" in recommendation:
        return "⚠️"
    else:
        return "❌"

def get_originality_emoji(conclusion):
    """根据原创度结论返回表情符号"""
    if "原创" in conclusion:
        return "✅"
    elif "结构雷同" in conclusion:
        return "⚠️"
    else:
        return "❌"

# 主界面
st.title("📋 质量审核与原创度检测")
st.markdown("**支持文字输入 + 图片上传（AI识别）**")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统配置")
    st.info(f"**GPT模型**: {OPENAI_MODEL}")
    st.success(f"**Vision模型**: Mistral Pixtral 📷")
    if DUAL_MODEL_ENABLED:
        st.success(f"**DeepSeek R1**: {DEEPSEEK_MODEL} ✅")
        st.info("🌐 R1 支持联网搜索")
    else:
        st.warning("**DeepSeek**: 未配置")
    
    st.markdown("---")
    st.header("📊 功能说明")
    st.markdown("""
    ### 📝 输入方式
    1. **文字输入** - 直接输入题目
    2. **图片上传** - 上传截图/照片
       - AI自动识别
       - 支持手写和印刷
       - 识别后可编辑
    
    ### 1️⃣ 质量审核
    - 清晰度 (0-2分)
    - 数学严谨性 (0-2分)
    - 完整性 (0-2分)
    - 可解性 (0-2分)
    - 教育价值 (0-2分)
    
    ### 2️⃣ 原创度检测
    - 🤖 双模型交叉验证
    - 📊 结果对比分析
    - 🔍 来源链接追溯
    """)

# 主内容
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 输入数学题目")
    
    # 选择输入方式
    input_method = st.radio(
        "选择输入方式：",
        ["💬 文字输入", "📷 图片上传"],
        horizontal=True
    )
    
    problem_text = ""
    
    if input_method == "💬 文字输入":
        # 文字输入
        problem_text = st.text_area(
            "题目内容",
            height=300,
            placeholder="请输入要审核的数学题目...\n\n例如：\n在直角三角形中，两条直角边长度分别为3和4，求斜边长度。",
            key="text_input"
        )
    
    else:
        # 图片上传
        st.markdown("#### 📷 上传题目图片")
        st.info("💡 支持：截图、拍照、扫描件")
        
        uploaded_file = st.file_uploader(
            "选择图片文件",
            type=["png", "jpg", "jpeg", "webp"],
            help="支持 PNG、JPG、JPEG、WEBP 格式"
        )
        
        if uploaded_file is not None:
            # 显示上传的图片
            image = Image.open(uploaded_file)
            st.image(image, caption="上传的图片", use_container_width=True)
            
            # OCR 识别按钮
            if st.button("🤖 AI识别题目", type="primary", use_container_width=True):
                with st.spinner("🔍 Mistral Pixtral 正在识别图片中的题目..."):
                    extracted_text = extract_text_from_image(uploaded_file)
                    st.session_state['extracted_text'] = extracted_text
            
            # 显示识别结果（可编辑）
            if 'extracted_text' in st.session_state:
                st.markdown("#### ✅ 识别结果（可编辑）：")
                problem_text = st.text_area(
                    "识别的题目内容",
                    value=st.session_state['extracted_text'],
                    height=200,
                    help="AI识别的结果，如有错误可以直接编辑修改",
                    key="extracted_text_area"
                )
                
                if "❌" in problem_text:
                    st.error("图片识别失败，请重新上传或使用文字输入")
                    problem_text = ""
    
    # 审核按钮
    st.markdown("---")
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        review_button = st.button("📊 质量审核", type="primary", use_container_width=True)
    
    with button_col2:
        originality_button = st.button("🔎 原创度检测（双模型）", type="secondary", use_container_width=True)

with col2:
    st.header("📊 分析结果")
    
    # 质量审核
    if review_button:
        if not problem_text or not problem_text.strip():
            st.error("⚠️ 请输入题目内容或上传图片！")
        else:
            with st.spinner("🤔 GPT-5.1 正在分析题目质量..."):
                prompt = REVIEW_PROMPT_TEMPLATE.format(problem_text=problem_text)
                result = call_openai_api(prompt, OPENAI_API_KEY, OPENAI_MODEL)
                
                try:
                    if isinstance(result, str):
                        review_data = json.loads(result)
                    else:
                        review_data = result
                    
                    if "error" in review_data:
                        st.error(f"❌ API 调用失败: {review_data['error']}")
                    else:
                        total_score = review_data.get('total_score', 0)
                        recommendation = review_data.get('recommendation', 'UNKNOWN')
                        
                        st.markdown(f"### {get_recommendation_emoji(recommendation)} 质量审核结果")
                        
                        score_col1, score_col2 = st.columns([1, 2])
                        with score_col1:
                            st.metric("总分", f"{total_score}/10")
                        with score_col2:
                            st.markdown(f"**推荐**: {recommendation}")
                        
                        st.markdown("---")
                        st.markdown("#### 📈 详细评分")
                        
                        score_items = [
                            ("清晰度", review_data.get('clarity_score', 0)),
                            ("数学严谨性", review_data.get('rigor_score', 0)),
                            ("完整性", review_data.get('completeness_score', 0)),
                            ("可解性", review_data.get('solvability_score', 0)),
                            ("教育价值", review_data.get('educational_value_score', 0))
                        ]
                        
                        for label, score in score_items:
                            progress = score / 2.0
                            st.progress(progress, text=f"{label}: {score}/2")
                        
                        st.markdown("---")
                        st.markdown("#### 💡 评审理由")
                        st.write(review_data.get('reasoning', '无'))
                        
                        issues = review_data.get('issues', [])
                        if issues:
                            st.markdown("#### ⚠️ 发现的问题")
                            for issue in issues:
                                st.warning(f"• {issue}")
                        else:
                            st.success("✨ 未发现明显问题！")
                
                except json.JSONDecodeError:
                    st.error("❌ 无法解析 API 返回结果")
    
    # 原创度检测（双模型）
    elif originality_button:
        if not problem_text or not problem_text.strip():
            st.error("⚠️ 请输入题目内容或上传图片！")
        else:
            st.markdown("### 🤖 双模型原创度检测")
            
            # 为不同模型使用不同的 Prompt
            gpt_prompt = ORIGINALITY_PROMPT_GPT.format(problem_text=problem_text)
            deepseek_prompt = ORIGINALITY_PROMPT_DEEPSEEK.format(problem_text=problem_text)
            
            # GPT-5.1 检测
            with st.spinner("🔍 GPT-5.1 正在检测..."):
                gpt_result = call_openai_api(gpt_prompt, OPENAI_API_KEY, OPENAI_MODEL)
            
            # DeepSeek R1 检测（使用强调准确性的 Prompt）
            deepseek_result = None
            if DUAL_MODEL_ENABLED:
                with st.spinner("🔍 DeepSeek R1 正在检测（已启用严格验证模式）..."):
                    deepseek_result = call_openai_api(
                        deepseek_prompt, 
                        DEEPSEEK_API_KEY, 
                        DEEPSEEK_MODEL,
                        base_url="https://api.deepseek.com"
                    )
            
            # 显示结果
            tab1, tab2, tab3 = st.tabs(["📊 对比总结", "🤖 GPT-5.1", "🌐 DeepSeek R1"])
            
            with tab1:
                st.markdown("#### 🎯 双模型对比")
                
                try:
                    gpt_data = json.loads(gpt_result) if isinstance(gpt_result, str) else gpt_result
                    
                    if deepseek_result:
                        ds_data = json.loads(deepseek_result) if isinstance(deepseek_result, str) else deepseek_result
                        
                        gpt_conclusion = gpt_data.get('originality_conclusion', 'UNKNOWN')
                        ds_conclusion = ds_data.get('originality_conclusion', 'UNKNOWN')
                        
                        st.markdown("##### 🔍 检测结论对比")
                        comp_col1, comp_col2, comp_col3 = st.columns(3)
                        
                        with comp_col1:
                            st.metric("GPT-5.1", gpt_conclusion, 
                                     delta=get_originality_emoji(gpt_conclusion))
                        
                        with comp_col2:
                            st.metric("DeepSeek R1 🌐", ds_conclusion,
                                     delta=get_originality_emoji(ds_conclusion))
                        
                        with comp_col3:
                            if gpt_conclusion == ds_conclusion:
                                st.success("✅ 结论一致\n高可信度")
                            else:
                                st.warning("⚠️ 结论不同\n需人工判断")
                        
                        st.markdown("---")
                        st.info("💡 **建议**: 查看各模型的详细分析（切换到对应标签页）")
                    
                    else:
                        st.markdown("##### 🔍 检测结论")
                        conclusion = gpt_data.get('originality_conclusion', 'UNKNOWN')
                        st.metric("GPT-5.1", conclusion, 
                                 delta=get_originality_emoji(conclusion))
                        st.info("💡 配置 DeepSeek API Key 后可启用双模型对比")
                
                except Exception as e:
                    st.error(f"❌ 解析结果失败: {e}")
            
            # GPT-5.1 详细结果
            with tab2:
                try:
                    gpt_data = json.loads(gpt_result) if isinstance(gpt_result, str) else gpt_result
                    
                    if "error" in gpt_data:
                        st.error(f"❌ GPT-5.1 调用失败: {gpt_data['error']}")
                    else:
                        conclusion = gpt_data.get('originality_conclusion', 'UNKNOWN')
                        st.markdown(f"### {get_originality_emoji(conclusion)} {conclusion}")
                        
                        similar_problems = gpt_data.get('similar_problems', [])
                        if similar_problems:
                            st.markdown("#### 🔍 发现的相似题目")
                            for idx, prob in enumerate(similar_problems[:3], 1):
                                with st.expander(f"相似题目 {idx} - 相似度: {prob.get('similarity_percentage', 0)}%"):
                                    st.markdown(f"**来源**: {prob.get('source', '未知')}")
                                    source_url = prob.get('source_url', '')
                                    if source_url and source_url.strip():
                                        if source_url.startswith('http'):
                                            st.markdown(f"**链接**: [{source_url}]({source_url})")
                                        else:
                                            st.markdown(f"**详细出处**: {source_url}")
                                    st.markdown(f"**题目内容**: {prob.get('content', '无')}")
                                    st.markdown(f"**相似原因**: {prob.get('similarity_reason', '无')}")
                        else:
                            st.success("✅ 未发现高度相似的题目")
                        
                        unique_aspects = gpt_data.get('unique_aspects', [])
                        if unique_aspects:
                            st.markdown("#### ✨ 题目的独特之处")
                            for aspect in unique_aspects:
                                st.success(f"• {aspect}")
                        
                        if gpt_data.get('overall_assessment'):
                            st.markdown("---")
                            st.info(f"📝 **整体评估**: {gpt_data['overall_assessment']}")
                
                except Exception as e:
                    st.error(f"❌ 解析 GPT-5.1 结果失败: {e}")
            
            # DeepSeek 详细结果
            with tab3:
                if not DUAL_MODEL_ENABLED:
                    st.warning("⚠️ DeepSeek 未配置")
                elif not deepseek_result:
                    st.error("❌ DeepSeek 调用失败")
                else:
                    # 添加警告提示
                    st.warning("""
                    ⚠️ **DeepSeek R1 结果验证提醒**：
                    - 请务必验证所有来源链接的真实性
                    - AI模型可能产生不准确的来源信息
                    - 建议人工核实后再做判断
                    """)
                    
                    try:
                        ds_data = json.loads(deepseek_result) if isinstance(deepseek_result, str) else deepseek_result
                        
                        if "error" in ds_data:
                            st.error(f"❌ DeepSeek 调用失败: {ds_data['error']}")
                        else:
                            conclusion = ds_data.get('originality_conclusion', 'UNKNOWN')
                            st.markdown(f"### {get_originality_emoji(conclusion)} {conclusion}")
                            
                            similar_problems = ds_data.get('similar_problems', [])
                            if similar_problems:
                                st.markdown("#### 🔍 发现的相似题目")
                                for idx, prob in enumerate(similar_problems[:3], 1):
                                    # 获取置信度
                                    confidence = prob.get('confidence_level', '未知')
                                    confidence_emoji = {
                                        '高': '🟢',
                                        '中': '🟡', 
                                        '低': '🔴',
                                        '未知': '⚪'
                                    }.get(confidence, '⚪')
                                    
                                    with st.expander(f"相似题目 {idx} - 相似度: {prob.get('similarity_percentage', 0)}% {confidence_emoji} 置信度: {confidence}"):
                                        st.markdown(f"**来源**: {prob.get('source', '未知')}")
                                        source_url = prob.get('source_url', '')
                                        if source_url and source_url.strip():
                                            # 提醒用户验证链接
                                            if '待确认' in source_url or not source_url.startswith('http'):
                                                st.warning(f"⚠️ **出处**: {source_url}（需人工验证）")
                                            else:
                                                st.markdown(f"**链接**: [{source_url}]({source_url}) ⚠️ *请验证链接有效性*")
                                        st.markdown(f"**题目内容**: {prob.get('content', '无')}")
                                        st.markdown(f"**相似原因**: {prob.get('similarity_reason', '无')}")
                            else:
                                st.success("✅ 未发现高度相似的题目")
                            
                            # 显示检索说明（如果有）
                            search_note = ds_data.get('search_note', '')
                            if search_note:
                                st.info(f"🔍 **检索说明**: {search_note}")
                    
                    except Exception as e:
                        st.error(f"❌ 解析 DeepSeek 结果失败: {e}")
    
    else:
        st.info("""
        👈 请在左侧选择输入方式：
        
        **💬 文字输入** - 直接输入题目文字
        
        **📷 图片上传** - 上传截图或照片
        - 上传图片后点击"AI识别"
        - 识别结果可以编辑修改
        - 然后选择审核功能
        """)

# 底部说明
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p><strong>数学题目审核系统</strong> - 质量审核与原创度检测</p>
    <p>支持文字输入 + 图片上传 | GPT-5.1 + DeepSeek R1 | Mistral Pixtral OCR</p>
</div>
""", unsafe_allow_html=True)

