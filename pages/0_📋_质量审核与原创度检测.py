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

# 注意：环境变量已在主 app.py 中加载

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

# DeepSeek R1 暂时禁用（准确性问题）
DUAL_MODEL_ENABLED = False

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

# 原创度检测 Prompt - DeepSeek R1 版本（平衡准确性与查重能力）
ORIGINALITY_PROMPT_DEEPSEEK = """你是一名严谨的学术查重专家。你的任务是分析题目的原创度。

⚠️ **重要原则**：
1. **准确性第一**：不要编造不存在的具体链接（如完整URL）
2. **可以发现相似性**：如果题目结构、逻辑、考点与你知识库中的内容相似，应该指出
3. **来源分级处理**：
   - ✅ **确定来源**：如果你明确知道来自某本教材、某个竞赛、某个知名题库，可以说明（但不要编造具体页码或题号）
   - ⚠️ **结构相似**：如果只是发现题目类型、解题思路相似，但记不清具体出处，可以说"结构雷同"并分析相似点
   - ❌ **原创**：如果确实没有印象，才判定为原创

**重要：请严格按照 JSON 格式输出结果（JSON format required）。**

**题目内容**:
{problem_text}

**检索策略**:
1. 分析题目的核心考点、逻辑结构、设定背景
2. 在你的知识库中搜索类似的题目或题型
3. 如果发现相似内容：
   - 说明相似之处（考点、结构、设定等）
   - 如果记得大致来源（如"高考真题""AMC竞赛""微积分教材"），可以说明
   - 如果不记得具体出处，就说"来源：记忆中见过类似题型，但无法提供准确出处"
4. **绝对不要编造完整的URL、具体的题号、页码**

**输出格式（JSON format）**:
请严格按照以下 JSON 结构输出：

{{
  "originality_conclusion": "原创 / 疑似搬运 / 结构雷同",
  "similar_problems": [
    {{
      "source": "来源类型（如'高考真题''竞赛题库''微积分教材'等，如果只是题型相似就写'常见题型'）",
      "source_url": "【如果你确切知道来源】写详细出处（如'2018年全国卷I''AMC 12 2020'）；【如果不确定具体出处】写'记忆中见过类似，但无准确出处'；【绝对不要】编造具体网址链接",
      "content": "相似题目的核心特征描述（不要给出完整题目）",
      "similarity_percentage": 70,
      "similarity_reason": "详细说明相似之处（考点、结构、逻辑、设定等）",
      "confidence_level": "高（确定见过）/中（印象中有类似）/低（仅题型相似）"
    }}
  ],
  "unique_aspects": ["列出题目的独特之处或创新点"],
  "keyword_analysis": "核心考点和关键概念",
  "structure_analysis": "题目的逻辑结构和解题思路",
  "overall_assessment": "综合评估（既要指出相似性，也要指出独特性）",
  "search_note": "你的检索思路和判断依据"
}}

**输出要求**：
- ✅ **可以**指出题型、考点、结构的相似性
- ✅ **可以**说"高考常见题型""竞赛经典题型"等笼统来源
- ✅ **可以**说"记忆中见过类似，但无准确出处"
- ❌ **不要**编造完整的URL链接（如 https://...）
- ❌ **不要**编造具体的题号、页码（除非你100%确定）
- ❌ **不要**因为过于谨慎而把所有题目都判为"原创"

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

def call_openai_api(prompt, api_key, model, base_url="https://api.openai.com/v1", use_json_format=True):
    """调用 API（支持 OpenAI 和 DeepSeek）"""
    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        # 构建请求参数
        request_params = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        # 只有在明确要求 JSON 格式时才添加 response_format
        if use_json_format:
            request_params["response_format"] = {"type": "json_object"}
        
        response = client.chat.completions.create(**request_params)
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
    st.info("💡 **原创度检测**: 仅使用 GPT-5.1")
    
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
    - 🤖 GPT-5.1 深度分析
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
        originality_button = st.button("🔎 原创度检测", type="secondary", use_container_width=True)

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
    
    # 原创度检测（GPT-5.1）
    elif originality_button:
        if not problem_text or not problem_text.strip():
            st.error("⚠️ 请输入题目内容或上传图片！")
        else:
            st.markdown("### 🔍 原创度检测结果")
            
            # 使用 GPT-5.1 检测
            gpt_prompt = ORIGINALITY_PROMPT_GPT.format(problem_text=problem_text)
            
            # GPT-5.1 检测
            with st.spinner("🔍 GPT-5.1 正在检测原创度..."):
                gpt_result = call_openai_api(gpt_prompt, OPENAI_API_KEY, OPENAI_MODEL)
            
            # 显示结果
            st.markdown("---")
            st.markdown("### 📊 原创度检测结果")
            
            try:
                gpt_data = json.loads(gpt_result) if isinstance(gpt_result, str) else gpt_result
                
                if "error" in gpt_data:
                    st.error(f"❌ GPT-5.1 调用失败: {gpt_data['error']}")
                else:
                    conclusion = gpt_data.get('originality_conclusion', 'UNKNOWN')
                    st.markdown(f"## {get_originality_emoji(conclusion)} {conclusion}")
                    
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
                st.error(f"❌ 解析结果失败: {e}")
    
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

