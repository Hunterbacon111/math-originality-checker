"""
Llama 3.1 风格的 CSS 样式
Meta AI 风格：深色背景 + 渐变边框 + 发光效果
"""

LLAMA_STYLE = """
<style>
/* ==================== 全局样式 ==================== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* 主容器背景 */
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0f1419 100%);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #ffffff;
}

/* 背景装饰光斑 */
.stApp::before {
    content: '';
    position: fixed;
    top: -200px;
    right: -200px;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(65, 88, 208, 0.15) 0%, transparent 70%);
    filter: blur(80px);
    pointer-events: none;
    z-index: 0;
}

.stApp::after {
    content: '';
    position: fixed;
    bottom: -300px;
    left: -300px;
    width: 700px;
    height: 700px;
    background: radial-gradient(circle, rgba(200, 80, 192, 0.12) 0%, transparent 70%);
    filter: blur(100px);
    pointer-events: none;
    z-index: 0;
}

/* ==================== 侧边栏样式 ==================== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d15 0%, #1a1a2e 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

section[data-testid="stSidebar"] > div {
    background: transparent;
}

/* 侧边栏文字 */
section[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}

/* ==================== 标题样式 ==================== */
h1, h2, h3 {
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    background: linear-gradient(135deg, #4158D0 0%, #C850C0 50%, #FFCC70 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1.5rem !important;
}

h1 {
    font-size: 3rem !important;
    text-shadow: 0 0 40px rgba(65, 88, 208, 0.3);
}

h2 {
    font-size: 2rem !important;
}

h3 {
    font-size: 1.5rem !important;
}

/* ==================== 卡片/容器样式 ==================== */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    background: rgba(26, 26, 42, 0.6);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}

div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:hover {
    border-color: rgba(65, 88, 208, 0.5);
    box-shadow: 0 8px 40px rgba(65, 88, 208, 0.2), 0 0 60px rgba(200, 80, 192, 0.1);
    transform: translateY(-2px);
}

/* ==================== 按钮样式 ==================== */
.stButton > button {
    background: linear-gradient(135deg, #4158D0 0%, #C850C0 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 20px rgba(65, 88, 208, 0.4) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    box-shadow: 0 6px 30px rgba(65, 88, 208, 0.6), 0 0 40px rgba(200, 80, 192, 0.4) !important;
    transform: translateY(-2px) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

/* 次要按钮 */
.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, rgba(65, 88, 208, 0.2) 0%, rgba(200, 80, 192, 0.2) 100%) !important;
    border: 1px solid rgba(65, 88, 208, 0.5) !important;
}

/* ==================== 输入框样式 ==================== */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(26, 26, 42, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    padding: 0.75rem 1rem !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(65, 88, 208, 0.8) !important;
    box-shadow: 0 0 20px rgba(65, 88, 208, 0.3) !important;
}

/* ==================== 文件上传样式 ==================== */
div[data-testid="stFileUploader"] {
    background: rgba(26, 26, 42, 0.6) !important;
    border: 2px dashed rgba(65, 88, 208, 0.5) !important;
    border-radius: 16px !important;
    padding: 2rem !important;
}

div[data-testid="stFileUploader"]:hover {
    border-color: rgba(200, 80, 192, 0.7) !important;
    background: rgba(26, 26, 42, 0.8) !important;
}

/* ==================== 选项卡样式 ==================== */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(26, 26, 42, 0.5);
    border-radius: 12px;
    padding: 0.5rem;
}

.stTabs [data-baseweb="tab"] {
    color: rgba(255, 255, 255, 0.6) !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 500 !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(65, 88, 208, 0.3) 0%, rgba(200, 80, 192, 0.3) 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(65, 88, 208, 0.5) !important;
}

/* ==================== 指标卡片样式 ==================== */
div[data-testid="stMetric"] {
    background: rgba(26, 26, 42, 0.6);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

div[data-testid="stMetric"]:hover {
    border-color: rgba(65, 88, 208, 0.6);
    box-shadow: 0 0 30px rgba(65, 88, 208, 0.3);
}

div[data-testid="stMetric"] label {
    color: rgba(255, 255, 255, 0.7) !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

/* ==================== 展开面板样式 ==================== */
.streamlit-expanderHeader {
    background: rgba(26, 26, 42, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}

.streamlit-expanderHeader:hover {
    border-color: rgba(65, 88, 208, 0.5) !important;
    box-shadow: 0 0 20px rgba(65, 88, 208, 0.2) !important;
}

/* ==================== 消息框样式 ==================== */
.stSuccess, .stInfo, .stWarning, .stError {
    background: rgba(26, 26, 42, 0.8) !important;
    border-left: 4px solid !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px) !important;
}

.stSuccess {
    border-left-color: #10b981 !important;
}

.stInfo {
    border-left-color: #3b82f6 !important;
}

.stWarning {
    border-left-color: #f59e0b !important;
}

.stError {
    border-left-color: #ef4444 !important;
}

/* ==================== 进度条样式 ==================== */
.stProgress > div > div {
    background: linear-gradient(90deg, #4158D0 0%, #C850C0 50%, #FFCC70 100%) !important;
    border-radius: 10px !important;
    box-shadow: 0 0 20px rgba(65, 88, 208, 0.5) !important;
}

/* ==================== Spinner 加载动画 ==================== */
.stSpinner > div {
    border-top-color: #4158D0 !important;
    border-right-color: #C850C0 !important;
}

/* ==================== 选择器样式 ==================== */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: rgba(26, 26, 42, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
}

/* ==================== 单选按钮样式 ==================== */
.stRadio > div {
    background: rgba(26, 26, 42, 0.4);
    border-radius: 12px;
    padding: 1rem;
}

.stRadio label {
    color: #ffffff !important;
}

/* ==================== 滚动条样式 ==================== */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(26, 26, 42, 0.3);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #4158D0 0%, #C850C0 100%);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #5168E0 0%, #D860D2 100%);
}

/* ==================== 链接样式 ==================== */
a {
    color: #C850C0 !important;
    text-decoration: none !important;
    transition: all 0.3s ease !important;
}

a:hover {
    color: #FFCC70 !important;
    text-shadow: 0 0 10px rgba(255, 204, 112, 0.5) !important;
}

/* ==================== 代码块样式 ==================== */
code {
    background: rgba(26, 26, 42, 0.8) !important;
    border: 1px solid rgba(65, 88, 208, 0.3) !important;
    border-radius: 6px !important;
    color: #FFCC70 !important;
    padding: 0.2rem 0.5rem !important;
}

pre {
    background: rgba(26, 26, 42, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
}

/* ==================== 表格样式 ==================== */
table {
    background: rgba(26, 26, 42, 0.6) !important;
    border-radius: 12px !important;
}

thead tr {
    background: rgba(65, 88, 208, 0.2) !important;
}

th {
    color: #ffffff !important;
    font-weight: 600 !important;
}

td {
    color: rgba(255, 255, 255, 0.9) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
}

/* ==================== 响应式调整 ==================== */
@media (max-width: 768px) {
    h1 {
        font-size: 2rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
    }
    
    .stButton > button {
        padding: 0.6rem 1.5rem !important;
        font-size: 0.9rem !important;
    }
}
</style>
"""

def apply_llama_style():
    """应用 Llama 3.1 风格到 Streamlit 应用"""
    import streamlit as st
    st.markdown(LLAMA_STYLE, unsafe_allow_html=True)

