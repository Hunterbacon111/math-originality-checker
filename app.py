#!/usr/bin/env python3
"""
数学题目审核系统 - 首页
"""
import streamlit as st

# 页面配置
st.set_page_config(
    page_title="数学题目审核系统",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 主标题
st.title("🔍 数学题目审核系统")
st.markdown("### 欢迎使用智能数学题目分析平台")

st.markdown("---")

# 功能介绍
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ## 📋 质量审核与原创度检测
    
    ### ✨ 核心功能
    - 📝 **智能输入**: 支持文字输入和图片上传（AI OCR识别）
    - 📊 **质量审核**: 5维度专业评分（清晰度、严谨性、完整性、可解性、教育价值）
    - 🔍 **原创度检测**: GPT-5.1 深度分析题目原创性
    - 🔗 **来源追溯**: 提供详细的相似题目来源链接
    
    ### 🛠️ 技术特性
    - **OCR识别**: Mistral Pixtral 高精度数学公式识别
    - **GPT-5.1**: OpenAI 最先进的AI模型
    - **实时分析**: 快速响应，秒级出结果
    
    ---
    
    👉 **[点击左侧导航栏进入 →](#)**
    """)

with col2:
    st.markdown("""
    ## 🎯 难度测试
    
    ### ✨ 核心功能
    - 📤 **题目上传**: 支持文字输入和图片上传
    - ✍️ **答案输入**: 提供官方标准答案
    - 🤖 **AI求解**: Doubao Seed 1.6 Thinking 深度推理
    - ⚡ **并行计算**: 多任务同时执行，大幅节省时间
    - 📊 **流式显示**: 每完成一次立即显示，实时反馈
    - 🎲 **多次测试**: 可选3-10次测试，结果更准确
    
    ### 💡 评估标准
    - ✅ **正确率 ≥ 80%**: 题目较为简单
    - ⚠️ **正确率 50-80%**: 难度适中
    - ❌ **正确率 < 50%**: 题目困难
    
    ### 🎓 适用场景
    - 试卷命题难度把控
    - 练习题难度分级
    - 竞赛题筛选
    
    ---
    
    👉 **[点击左侧导航栏进入 →](#)**
    """)

st.markdown("---")

# 系统状态
st.markdown("## ⚙️ 系统状态")

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    st.info("**GPT-5.1**\n✅ 已配置")

with status_col2:
    st.success("**Mistral Pixtral**\n✅ 图片识别")

with status_col3:
    st.success("**Doubao Seed 1.6**\n✅ Thinking模型")

st.markdown("---")

# 使用指南
with st.expander("📖 使用指南", expanded=False):
    st.markdown("""
    ### 🚀 快速开始
    
    #### 1️⃣ 质量审核与原创度检测
    1. 点击左侧导航栏的 **"📋 质量审核与原创度检测"**
    2. 选择输入方式（文字或图片）
    3. 输入或上传题目
    4. 选择功能：
       - 点击 **"质量审核"** 查看详细评分
       - 点击 **"原创度检测"** 进行查重分析
    
    #### 2️⃣ 难度测试
    1. 点击左侧导航栏的 **"🎯 难度测试"**
    2. 输入或上传题目
    3. 输入官方标准答案
    4. 选择测试次数（建议6-8次）
    5. 点击 **"开始难度测试"**
    6. 查看AI求解统计结果
    
    ### 💡 使用技巧
    - **图片上传**: 确保图片清晰，公式完整
    - **标准答案**: 简洁明确，便于AI比对
    - **测试次数**: 次数越多，结果越准确（并行计算不影响速度）
    - **原创度检测**: GPT-5.1 提供可靠的查重分析
    - **实时观察**: 观察每次求解的即时结果，及时发现问题
    
    ### 🔧 常见问题
    - **识别失败**: 尝试重新上传更清晰的图片，或使用文字输入
    - **测试超时**: 减少测试次数或检查网络连接
    - **结果异常**: 刷新页面重新测试
    """)

# 底部信息
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p><strong>数学题目审核系统</strong> v1.1</p>
    <p>GPT-5.1 | Doubao Seed 1.6 Thinking | Mistral Pixtral</p>
    <p>支持文字输入 + 图片OCR识别 | AI智能分析</p>
</div>
""", unsafe_allow_html=True)
