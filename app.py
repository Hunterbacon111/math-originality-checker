#!/usr/bin/env python3
"""
数学题目质量审核与原创度检测系统 - Web 界面
使用 Streamlit 创建交互式界面
"""
import streamlit as st
import json
import time
import os
from openai import OpenAI

# 页面配置
st.set_page_config(
    page_title="数学题目审核系统",
    page_icon="🔍",
    layout="wide"
)

# OpenAI 配置 - 从环境变量读取
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5.1-chat-latest")

# 检查 API Key 是否配置
if not API_KEY:
    st.error("❌ 系统配置错误：未找到 OPENAI_API_KEY 环境变量")
    st.info("请联系管理员配置 API Key")
    st.stop()

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

# 原创度检测 Prompt
ORIGINALITY_PROMPT_TEMPLATE = """你现在是一名资深的学术查重专家和高级搜索工程专家。

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
  - 如果来自网站/论坛，提供完整的URL链接（如：https://artofproblemsolving.com/community/...）
  - 如果来自书籍/试卷，提供详细出处（如：《高等数学》第7版 第3章 例题5.2）
  - 如果来自竞赛，提供年份和题号（如：2018 AMC 12A Problem 15）
- 分析题目的独特之处

**题目内容**:
{problem_text}

**输出格式 (Output Format)**:
请以 JSON 格式输出，包含以下字段：

{{
  "originality_conclusion": "原创 / 疑似搬运 / 结构雷同",
  "similar_problems": [
    {{
      "source": "来源名称（如：AOPS论坛、高考2018年全国卷I）",
      "source_url": "具体链接或详细出处（如果有）",
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

def call_gpt_api(prompt):
    """调用 GPT API"""
    try:
        client = OpenAI(api_key=API_KEY)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return {"error": str(e)}

def get_score_color(score):
    """根据分数返回颜色"""
    if score >= 7:
        return "green"
    elif score >= 5:
        return "orange"
    else:
        return "red"

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
st.title("🔍 数学题目审核系统")
st.markdown("**质量审核 + 原创度检测**")
st.markdown("---")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 系统配置")
    st.info(f"**模型**: {MODEL_NAME}")
    
    st.markdown("---")
    st.header("📊 功能说明")
    
    st.markdown("### 1️⃣ 质量审核")
    st.markdown("""
    评估题目的：
    - **清晰度** (0-2分)
    - **数学严谨性** (0-2分)
    - **完整性** (0-2分)
    - **可解性** (0-2分)
    - **教育价值** (0-2分)
    
    **总分**: 0-10分
    """)
    
    st.markdown("### 2️⃣ 原创度检测")
    st.markdown("""
    检测题目的原创性：
    - 查找相似题目
    - 提供来源链接
    - 分析结构雷同
    - 评估独特性
    
    **结论**: 原创/疑似搬运/结构雷同
    """)
    
    st.markdown("---")
    st.markdown("*Powered by OpenAI GPT-5.1*")

# 主内容区域
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 输入数学题目")
    
    # 题目输入
    problem_text = st.text_area(
        "题目内容",
        height=300,
        placeholder="请输入要审核的数学题目...\n\n例如：\n求解方程：3x + 5 = 20，求 x 的值。"
    )
    
    # 审核按钮
    st.markdown("---")
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        review_button = st.button("📊 质量审核", type="primary", use_container_width=True)
    
    with button_col2:
        originality_button = st.button("🔎 原创度检测", type="secondary", use_container_width=True)

with col2:
    st.header("📊 分析结果")
    
    # 质量审核功能
    if review_button:
        if not problem_text.strip():
            st.error("⚠️ 请输入题目内容！")
        else:
            with st.spinner("🤔 GPT-5.1 正在分析题目质量..."):
                prompt = REVIEW_PROMPT_TEMPLATE.format(problem_text=problem_text)
                result = call_gpt_api(prompt)
                
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
                        
                        st.markdown("---")
                        result_json = json.dumps(review_data, ensure_ascii=False, indent=2)
                        st.download_button(
                            label="📥 下载审核结果 (JSON)",
                            data=result_json,
                            file_name="quality_review_result.json",
                            mime="application/json"
                        )
                        
                except json.JSONDecodeError:
                    st.error("❌ 无法解析 API 返回结果")
                    st.code(result)
    
    # 原创度检测功能
    elif originality_button:
        if not problem_text.strip():
            st.error("⚠️ 请输入题目内容！")
        else:
            with st.spinner("🔎 GPT-5.1 正在检测题目原创度..."):
                prompt = ORIGINALITY_PROMPT_TEMPLATE.format(problem_text=problem_text)
                result = call_gpt_api(prompt)
                
                try:
                    if isinstance(result, str):
                        originality_data = json.loads(result)
                    else:
                        originality_data = result
                    
                    if "error" in originality_data:
                        st.error(f"❌ API 调用失败: {originality_data['error']}")
                    else:
                        conclusion = originality_data.get('originality_conclusion', 'UNKNOWN')
                        
                        st.markdown(f"### {get_originality_emoji(conclusion)} 原创度检测结果")
                        st.markdown(f"**查重结论**: {conclusion}")
                        
                        st.markdown("---")
                        
                        # 相似题目展示
                        similar_problems = originality_data.get('similar_problems', [])
                        if similar_problems and len(similar_problems) > 0:
                            st.markdown("#### 🔍 发现的相似题目")
                            for idx, prob in enumerate(similar_problems[:3], 1):
                                with st.expander(f"相似题目 {idx} - 相似度: {prob.get('similarity_percentage', 0)}%"):
                                    st.markdown(f"**来源**: {prob.get('source', '未知')}")
                                    
                                    # 显示来源链接
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
                        
                        st.markdown("---")
                        
                        # 独特之处
                        unique_aspects = originality_data.get('unique_aspects', [])
                        if unique_aspects:
                            st.markdown("#### ✨ 题目的独特之处")
                            for aspect in unique_aspects:
                                st.success(f"• {aspect}")
                        
                        st.markdown("---")
                        
                        # 关键词分析
                        keyword_analysis = originality_data.get('keyword_analysis', '')
                        if keyword_analysis:
                            st.markdown("#### 🔑 关键词分析")
                            st.write(keyword_analysis)
                        
                        # 结构分析
                        structure_analysis = originality_data.get('structure_analysis', '')
                        if structure_analysis:
                            st.markdown("#### 🏗️ 结构分析")
                            st.write(structure_analysis)
                        
                        # 整体评估
                        overall_assessment = originality_data.get('overall_assessment', '')
                        if overall_assessment:
                            st.markdown("---")
                            st.markdown("#### 📝 整体评估")
                            st.info(overall_assessment)
                        
                        st.markdown("---")
                        result_json = json.dumps(originality_data, ensure_ascii=False, indent=2)
                        st.download_button(
                            label="📥 下载原创度报告 (JSON)",
                            data=result_json,
                            file_name="originality_report.json",
                            mime="application/json"
                        )
                        
                except json.JSONDecodeError:
                    st.error("❌ 无法解析 API 返回结果")
                    st.code(result)
    
    else:
        st.info("👈 请在左侧输入题目并选择功能：\n\n📊 **质量审核** - 评估题目质量\n\n🔎 **原创度检测** - 检测题目原创性")

# 底部说明
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p><strong>数学题目审核系统</strong> - 使用 OpenAI GPT-5.1 提供智能分析</p>
    <p>质量审核 | 原创度检测 | 不提供解题答案</p>
</div>
""", unsafe_allow_html=True)
