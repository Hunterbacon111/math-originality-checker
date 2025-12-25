#!/usr/bin/env python3
"""
数学题目难度测试系统
使用 Doubao Seed 1.6 Thinking 模型多次求解题目，统计正确率来评估难度
支持并行计算和流式结果显示
"""
import streamlit as st
import json
import os
import base64
import io
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from PIL import Image
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="难度测试 - 数学题目审核系统",
    page_icon="🎯",
    layout="wide"
)

# API 配置
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
DOUBAO_API_KEY_1 = os.getenv("DOUBAO_API_KEY_1")  # Doubao 一号
DOUBAO_API_KEY_2 = os.getenv("DOUBAO_API_KEY_2")  # Doubao 二号
DOUBAO_MODEL_1 = "ep-m-20251211112628-2r5n6"  # Doubao 一号端点
DOUBAO_MODEL_2 = "ep-m-20251225141150-hfztd"  # Doubao 二号端点
MISTRAL_VISION_MODEL = "pixtral-large-latest"

# 检查配置
if not DOUBAO_API_KEY_1 and not DOUBAO_API_KEY_2:
    st.error("❌ 未配置任何 DOUBAO_API_KEY")
    st.info("请在服务器的 .env 文件中添加：DOUBAO_API_KEY_1 和/或 DOUBAO_API_KEY_2")
    st.stop()

# 确定可用的 API（名称、API Key、端点ID）
AVAILABLE_APIS = []
if DOUBAO_API_KEY_1:
    AVAILABLE_APIS.append(("🤖 Doubao 一号", DOUBAO_API_KEY_1, DOUBAO_MODEL_1))
if DOUBAO_API_KEY_2:
    AVAILABLE_APIS.append(("🤖 Doubao 二号", DOUBAO_API_KEY_2, DOUBAO_MODEL_2))

def encode_image_to_base64(image_file):
    """将上传的图片转换为 base64"""
    image = Image.open(image_file)
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def extract_text_from_image(image_file):
    """使用 Mistral Pixtral 从图片中提取数学题目"""
    if not MISTRAL_API_KEY:
        return "❌ 未配置 MISTRAL_API_KEY，无法识别图片"
    
    try:
        client = OpenAI(
            api_key=MISTRAL_API_KEY,
            base_url="https://api.mistral.ai/v1"
        )
        
        base64_image = encode_image_to_base64(image_file)
        
        response = client.chat.completions.create(
            model=MISTRAL_VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请提取图片中的数学题目，保持原格式和所有数学符号。只输出题目内容，不要解答。"
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
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"❌ 图片识别失败: {str(e)}"

def solve_problem_with_doubao(problem_text, attempt_number, api_key, model_id):
    """使用 Doubao Seed 1.6 Thinking 模型求解题目（单次）"""
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://ark.cn-beijing.volces.com/api/v3"
        )
        
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的数学问题求解助手。请仔细阅读题目，深入思考，给出详细的解题步骤和最终答案。最终答案请用【答案：】标记。"
                },
                {
                    "role": "user",
                    "content": f"请解答以下数学题目：\n\n{problem_text}"
                }
            ],
            temperature=0.7
        )
        
        elapsed_time = time.time() - start_time
        
        return {
            "attempt": attempt_number,
            "answer": response.choices[0].message.content,
            "success": True,
            "elapsed_time": elapsed_time
        }
    
    except Exception as e:
        return {
            "attempt": attempt_number,
            "answer": f"❌ 求解失败: {str(e)}",
            "success": False,
            "elapsed_time": 0
        }

def compare_answers(model_answer, correct_answer):
    """判断模型答案是否与标准答案一致"""
    try:
        # 检查是否有API错误
        if "❌" in model_answer and "求解失败" in model_answer:
            return False
        
        # 标准化处理
        model_answer_clean = model_answer.lower().strip()
        correct_answer_clean = correct_answer.lower().strip()
        
        # 提取【答案：】标记后的内容
        if "【答案：" in model_answer:
            model_answer_clean = model_answer.split("【答案：")[1].split("】")[0].strip().lower()
        elif "答案：" in model_answer:
            model_answer_clean = model_answer.split("答案：")[1].strip().split("\n")[0].strip().lower()
        
        # 移除空格和特殊字符进行比较
        import re
        model_clean = re.sub(r'[\s\$\{\}\\]', '', model_answer_clean)
        correct_clean = re.sub(r'[\s\$\{\}\\]', '', correct_answer_clean)
        
        # 多种比对方式
        # 1. 完全匹配
        if model_clean == correct_clean:
            return True
        
        # 2. 包含匹配
        if correct_clean in model_clean or model_clean in correct_clean:
            return True
        
        # 3. 数值匹配（提取数字）
        model_numbers = re.findall(r'-?\d+\.?\d*', model_answer_clean)
        correct_numbers = re.findall(r'-?\d+\.?\d*', correct_answer_clean)
        if model_numbers and correct_numbers:
            if model_numbers[0] == correct_numbers[0]:
                return True
        
        return False
    
    except Exception as e:
        return False

# 主界面
st.title("🎯 数学题目难度测试")
st.markdown("**通过 AI 模型多次求解，统计正确率来评估题目难度**")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 测试配置")
    st.success(f"**求解模型**: Doubao Seed 1.6 Thinking 🧠")
    
    # API 选择器
    if len(AVAILABLE_APIS) > 1:
        st.markdown("---")
        st.subheader("🤖 选择 API")
        api_choice = st.radio(
            "当前使用：",
            options=range(len(AVAILABLE_APIS)),
            format_func=lambda x: AVAILABLE_APIS[x][0],
            key="api_selector"
        )
        selected_api_name, selected_api_key, selected_model = AVAILABLE_APIS[api_choice]
        st.info(f"✅ 使用：**{selected_api_name}**")
    else:
        api_choice = 0
        selected_api_name, selected_api_key, selected_model = AVAILABLE_APIS[0]
        st.info(f"**API**: {selected_api_name} ✅")
    
    st.markdown("---")
    
    # API 状态显示
    st.subheader("📊 API 状态")
    for idx, (name, key, model) in enumerate(AVAILABLE_APIS):
        icon = "🟢" if idx == api_choice else "⚪"
        st.text(f"{icon} {name}")
    
    st.markdown("---")
    
    if MISTRAL_API_KEY:
        st.success("**图片识别**: Mistral Pixtral ✅")
    else:
        st.warning("**图片识别**: 未配置")
    
    st.markdown("---")
    st.header("📊 功能说明")
    st.markdown("""
    ### 🎯 难度评估原理
    使用 AI 模型多次求解同一题目：
    - ✅ 正确率高 → 题目简单
    - ⚠️ 正确率中等 → 难度适中
    - ❌ 正确率低 → 题目困难
    
    ### 🚀 技术特性
    - **并行计算**: 多个任务同时执行，大幅节省时间
    - **流式显示**: 每完成一次立即显示，实时反馈
    - **容错机制**: 单次失败不影响整体测试
    - **智能思考**: Seed 1.6 Thinking 深度推理
    
    ### 🔧 使用步骤
    1. 输入或上传题目
    2. 输入官方标准答案
    3. 选择测试次数（3-10次）
    4. 点击"开始测试"
    5. 实时查看每次求解结果
    6. 查看最终统计分析
    
    ### 💡 建议
    - 测试次数越多，结果越准确
    - 标准答案要简洁明确
    - 适合客观题测试
    - 并行计算最多8个任务同时运行
    """)

# 主内容区
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 输入题目与答案")
    
    # 选择输入方式
    input_method = st.radio(
        "题目输入方式：",
        ["💬 文字输入", "📷 图片上传"],
        horizontal=True
    )
    
    problem_text = ""
    
    if input_method == "💬 文字输入":
        problem_text = st.text_area(
            "题目内容",
            height=250,
            placeholder="请输入要测试难度的数学题目...\n\n例如：\n解方程：2x + 5 = 13",
            key="problem_input"
        )
    
    else:
        st.markdown("#### 📷 上传题目图片")
        uploaded_file = st.file_uploader(
            "选择图片文件",
            type=["png", "jpg", "jpeg", "webp"],
            help="支持 PNG、JPG、JPEG、WEBP 格式"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="上传的图片", use_container_width=True)
            
            if st.button("🤖 AI识别题目", type="primary", use_container_width=True):
                with st.spinner("🔍 Mistral Pixtral 正在识别..."):
                    extracted_text = extract_text_from_image(uploaded_file)
                    st.session_state['difficulty_test_problem'] = extracted_text
            
            if 'difficulty_test_problem' in st.session_state:
                st.markdown("#### ✅ 识别结果（可编辑）：")
                problem_text = st.text_area(
                    "识别的题目内容",
                    value=st.session_state['difficulty_test_problem'],
                    height=200,
                    key="extracted_problem"
                )
    
    st.markdown("---")
    
    # 标准答案输入
    correct_answer = st.text_area(
        "📌 官方标准答案",
        height=100,
        placeholder="请输入标准答案...\n\n例如：x = 4",
        help="答案要简洁明确，便于比对"
    )
    
    # 测试次数选择
    test_count = st.select_slider(
        "🔢 测试次数",
        options=[3, 4, 5, 6, 7, 8, 9, 10],
        value=6,
        help="选择让模型求解的次数，次数越多结果越准确"
    )
    
    st.markdown("---")
    
    # 开始测试按钮
    test_button = st.button("🚀 开始难度测试", type="primary", use_container_width=True)

with col2:
    st.header("📊 测试结果")
    
    if test_button:
        if not problem_text or not problem_text.strip():
            st.error("⚠️ 请输入题目内容！")
        elif not correct_answer or not correct_answer.strip():
            st.error("⚠️ 请输入标准答案！")
        else:
            # 显示测试信息
            st.info(f"🚀 使用 **{selected_api_name}** 启动 {test_count} 个并行任务，实时显示结果...")
            
            # 创建实时结果显示区域
            results_container = st.container()
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            # 存储结果
            results = []
            correct_count = 0
            completed_count = 0
            
            # 实时结果表格
            with results_container:
                st.markdown("#### 📊 实时测试进度")
                result_placeholder = st.empty()
            
            # 使用线程池进行并行计算
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=min(test_count, 8)) as executor:
                # 提交所有任务（使用选择的 API Key 和端点）
                futures = {
                    executor.submit(solve_problem_with_doubao, problem_text, i+1, selected_api_key, selected_model): i+1 
                    for i in range(test_count)
                }
                
                # 实时处理完成的任务
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        
                        if result["success"]:
                            # 判断是否正确
                            is_correct = compare_answers(result["answer"], correct_answer)
                            
                            if is_correct:
                                correct_count += 1
                            
                            results.append({
                                "attempt": result["attempt"],
                                "answer": result["answer"],
                                "correct": is_correct,
                                "elapsed_time": result["elapsed_time"]
                            })
                        else:
                            # 失败的任务
                            results.append({
                                "attempt": result["attempt"],
                                "answer": result["answer"],
                                "correct": False,
                                "elapsed_time": 0
                            })
                        
                        completed_count += 1
                        
                        # 更新进度条
                        progress_bar.progress(completed_count / test_count)
                        
                        # 实时显示状态
                        current_accuracy = (correct_count / completed_count) * 100 if completed_count > 0 else 0
                        status_text.text(
                            f"✅ 已完成: {completed_count}/{test_count} | "
                            f"✓ 正确: {correct_count} | "
                            f"当前正确率: {current_accuracy:.1f}%"
                        )
                        
                        # 实时更新结果表格
                        sorted_results = sorted(results, key=lambda x: x["attempt"])
                        result_data = []
                        for r in sorted_results:
                            # 判断结果状态
                            if "❌" in r["answer"] and "求解失败" in r["answer"]:
                                status = "🔴 API错误"
                                answer_preview = r["answer"][:50] + "..."
                            else:
                                icon = "✅" if r["correct"] else "❌"
                                status = f"{icon} {'正确' if r['correct'] else '错误'}"
                                # 提取答案预览
                                answer_text = r["answer"]
                                if "【答案：" in answer_text:
                                    answer_preview = answer_text.split("【答案：")[1].split("】")[0][:30]
                                elif "答案：" in answer_text:
                                    answer_preview = answer_text.split("答案：")[1].strip().split("\n")[0][:30]
                                else:
                                    answer_preview = answer_text[:30] + "..."
                            
                            time_str = f"{r['elapsed_time']:.1f}s" if r['elapsed_time'] > 0 else "-"
                            
                            result_data.append({
                                "测试": f"第 {r['attempt']} 次",
                                "状态": status,
                                "答案预览": answer_preview,
                                "耗时": time_str
                            })
                        
                        with result_placeholder:
                            st.dataframe(
                                result_data,
                                use_container_width=True,
                                hide_index=True
                            )
                    
                    except Exception as e:
                        st.error(f"任务执行出错: {str(e)}")
            
            total_time = time.time() - start_time
            
            # 清空进度显示
            status_text.empty()
            progress_bar.empty()
            
            # 显示完成信息
            st.success(f"🎉 全部测试完成！总耗时: {total_time:.1f} 秒")
            
            # 统计API错误次数
            api_error_count = sum(1 for r in results if "❌" in r["answer"] and "求解失败" in r["answer"])
            valid_count = test_count - api_error_count
            
            # 计算正确率（只计算有效测试）
            if valid_count > 0:
                accuracy = (correct_count / valid_count) * 100
            else:
                accuracy = 0
            
            # 显示统计结果
            st.markdown("### 🎯 测试统计")
            
            # 显示正确率
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric("总测试数", f"{test_count} 次")
            
            with metric_col2:
                st.metric("有效测试", f"{valid_count} 次")
            
            with metric_col3:
                st.metric("正确次数", f"{correct_count} 次", 
                         delta=f"{accuracy:.1f}%")
            
            with metric_col4:
                if api_error_count > 0:
                    st.metric("API错误", f"{api_error_count} 次", delta="需检查", delta_color="off")
                else:
                    if accuracy >= 80:
                        difficulty = "简单 😊"
                    elif accuracy >= 50:
                        difficulty = "中等 🤔"
                    else:
                        difficulty = "困难 😰"
                    st.metric("难度评估", difficulty)
            
            # 显示正确率条
            st.markdown("#### 📈 正确率")
            st.progress(accuracy / 100)
            
            st.markdown(f"**{accuracy:.1f}%** ({correct_count}/{test_count})")
            
            st.markdown("---")
            
            # 难度分析
            st.markdown("#### 💡 难度分析")
            
            if api_error_count > 0:
                st.warning(f"""
                ⚠️ **检测到 {api_error_count} 次API调用失败**
                
                **可能原因**：
                1. Doubao API 配置错误
                2. 网络连接问题
                3. API 配额不足或限流
                4. 模型端点配置错误
                
                **建议**：
                - 查看详细测试记录中的错误信息
                - 检查 DOUBAO_API_KEY 是否正确
                - 确认模型端点 ID 是否有效
                - 重新测试或减少并发数
                
                **有效测试结果**（{valid_count} 次）：
                - 正确：{correct_count} 次
                - 正确率：{accuracy:.1f}%
                """)
            
            if valid_count > 0:
                if accuracy >= 80:
                    st.success(f"""
                    ✅ **题目较为简单**
                    - AI 模型正确率达到 {accuracy:.1f}% ({correct_count}/{valid_count})
                    - 适合作为基础练习题
                    - 大部分学生应该能够掌握
                    """)
                elif accuracy >= 50:
                    st.warning(f"""
                    ⚠️ **题目难度适中**
                    - AI 模型正确率为 {accuracy:.1f}% ({correct_count}/{valid_count})
                    - 适合作为常规练习题
                    - 需要一定的思考和计算能力
                    """)
                else:
                    st.error(f"""
                    ❌ **题目较为困难**
                    - AI 模型正确率仅 {accuracy:.1f}% ({correct_count}/{valid_count})
                    - 适合作为挑战题或拔高题
                    - 需要较强的数学能力和解题技巧
                    
                    **建议检查**：
                    - 题目表述是否有歧义
                    - 标准答案格式是否匹配
                    - 查看详细记录了解模型的解答
                    """)
            else:
                st.error("❌ 所有测试都失败了，无法评估题目难度。请检查API配置。")
            
            st.markdown("---")
            
            # 详细结果展示
            with st.expander("📋 查看详细测试记录", expanded=False):
                sorted_results = sorted(results, key=lambda x: x["attempt"])
                for result in sorted_results:
                    # 判断是否是API错误
                    if "❌" in result["answer"] and "求解失败" in result["answer"]:
                        st.error(f"🔴 **第 {result['attempt']} 次测试 - API调用失败**")
                        st.code(result["answer"], language="text")
                    else:
                        icon = "✅" if result["correct"] else "❌"
                        correctness = "正确" if result["correct"] else "错误"
                        st.markdown(f"**{icon} 第 {result['attempt']} 次测试 - {correctness}** (耗时: {result['elapsed_time']:.1f}s)")
                        
                        # 显示模型的完整回答
                        st.text_area(
                            f"模型解答 {result['attempt']}",
                            value=result["answer"],
                            height=200,
                            key=f"result_{result['attempt']}"
                        )
                        
                        # 提取并高亮显示答案
                        if "【答案：" in result["answer"]:
                            extracted = result["answer"].split("【答案：")[1].split("】")[0]
                            st.info(f"📌 提取的答案：{extracted}")
                        elif "答案：" in result["answer"]:
                            extracted = result["answer"].split("答案：")[1].strip().split("\n")[0]
                            st.info(f"📌 提取的答案：{extracted}")
                    
                    st.markdown("---")
            
            # 标准答案对比
            st.markdown("#### 📌 标准答案")
            st.info(correct_answer)
    
    else:
        st.info("""
        👈 请在左侧：
        
        1️⃣ 输入或上传题目
        
        2️⃣ 输入官方标准答案
        
        3️⃣ 选择测试次数
        
        4️⃣ 点击"开始难度测试"
        
        系统将让 AI 模型多次求解题目，并统计正确率来评估难度。
        """)

# 底部说明
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p><strong>数学题目难度测试系统</strong></p>
    <p>基于 Doubao Seed 1.6 Thinking 模型多次求解统计</p>
</div>
""", unsafe_allow_html=True)

