#!/usr/bin/env python3
"""
题库管理系统 - 添加、查重、浏览题目
"""
import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from database import db

# 加载环境变量（Streamlit 多页面应用中每个页面都需要独立加载）
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="题库管理",
    page_icon="📚",
    layout="wide"
)

# API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.1-chat-latest")

# 检查配置
if not OPENAI_API_KEY:
    st.error("❌ 未配置 OPENAI_API_KEY")
    st.stop()

if not db.enabled:
    st.error("❌ Supabase 未配置或连接失败")
    st.info("请在 .env 文件中配置 SUPABASE_URL 和 SUPABASE_KEY")
    st.stop()

# 标题
st.title("📚 题库管理系统")
st.markdown("---")

# 创建标签页
tab1, tab2, tab3 = st.tabs(["➕ 添加题目", "📋 浏览题库", "📊 统计信息"])

# ==================== 标签页 1：添加题目 ====================
with tab1:
    st.markdown("### ➕ 添加题目到题库")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 基本信息
        st.markdown("#### 📝 基本信息")
        teacher_name = st.text_input("出题老师", placeholder="例如：张老师")
        problem_text = st.text_area("题目内容", height=150, placeholder="输入题目...")
        answer = st.text_area("答案", height=80, placeholder="输入答案...")
        solution = st.text_area("解析（解题过程）", height=100, placeholder="输入解题过程...")
        
        # 分类信息
        st.markdown("#### 🏷️ 分类信息")
        col_cat1, col_cat2 = st.columns(2)
        with col_cat1:
            category = st.selectbox(
                "类别",
                ["代数", "几何", "微积分", "概率统计", "数论", "其他"]
            )
        with col_cat2:
            tags_input = st.text_input("标签（用逗号分隔）", placeholder="例如：方程,一元一次方程")
    
    with col2:
        st.markdown("#### ⚙️ 可选操作")
        
        st.markdown("**🔍 查重检测**")
        check_duplicate = st.checkbox("添加前查重", value=True, help="使用 GPT-5.1 检测题库中是否有相似题目")
        
        st.markdown("**🎯 难度测试**")
        run_difficulty_test = st.checkbox("自动测试难度", value=False, help="使用 Doubao 模型测试题目难度")
        if run_difficulty_test:
            test_times = st.slider("测试次数", 3, 10, 6)
        
        st.markdown("**📊 质量审核**")
        run_quality_review = st.checkbox("质量审核", value=False, help="使用 GPT-5.1 评估题目质量")
    
    st.markdown("---")
    
    # 添加按钮
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn1:
        add_button = st.button("✓ 添加到题库", type="primary", use_container_width=True)
    with col_btn2:
        if check_duplicate:
            check_button = st.button("🔍 仅查重", use_container_width=True)
        else:
            check_button = False
    
    # 处理查重
    if check_button and problem_text:
        with st.spinner("🔍 正在查重..."):
            # 从数据库获取可能相似的题目
            similar_problems = db.search_similar_problems(problem_text, limit=30)
            
            if not similar_problems:
                st.success("✅ 题库为空或未发现完全相同的题目")
            else:
                st.info(f"📊 正在与 {len(similar_problems)} 道题目进行智能对比...")
                
                # 使用 GPT-5.1 逐个对比
                duplicate_found = []
                
                for existing_problem in similar_problems[:10]:  # 限制对比数量
                    try:
                        client = OpenAI(api_key=OPENAI_API_KEY)
                        
                        prompt = f"""你是一名数学题目查重专家。请判断以下两道题目是否相似。

新题目：
{problem_text}

已有题目：
{existing_problem['problem_text']}

请以 JSON 格式输出：
{{
  "is_similar": true/false,
  "similarity_percentage": 0-100,
  "reason": "相似原因说明"
}}

判断标准：
- 如果题目的核心考点、解题思路、数学结构相同，即使数字不同，也应判定为相似
- 相似度 >= 70% 视为重复
- 严格按照 JSON 格式输出
"""
                        
                        response = client.chat.completions.create(
                            model=OPENAI_MODEL,
                            messages=[{"role": "user", "content": prompt}],
                            response_format={"type": "json_object"}
                        )
                        
                        result = json.loads(response.choices[0].message.content)
                        
                        if result.get("is_similar") and result.get("similarity_percentage", 0) >= 70:
                            duplicate_found.append({
                                "problem": existing_problem,
                                "similarity": result.get("similarity_percentage"),
                                "reason": result.get("reason")
                            })
                    
                    except Exception as e:
                        st.warning(f"⚠️ 对比过程中出现错误: {e}")
                        continue
                
                # 显示查重结果
                if duplicate_found:
                    st.warning(f"⚠️ 发现 {len(duplicate_found)} 个相似题目")
                    
                    for idx, dup in enumerate(duplicate_found, 1):
                        with st.expander(f"相似题目 {idx} - 相似度: {dup['similarity']}%"):
                            st.markdown(f"**题目**: {dup['problem']['problem_text'][:200]}...")
                            st.markdown(f"**老师**: {dup['problem'].get('teacher_name', 'Unknown')}")
                            st.markdown(f"**类别**: {dup['problem'].get('category', 'Unknown')}")
                            st.markdown(f"**添加时间**: {dup['problem'].get('created_at', 'Unknown')}")
                            st.markdown(f"**相似原因**: {dup['reason']}")
                            
                            if dup['problem'].get('answer'):
                                st.markdown(f"**答案**: {dup['problem']['answer']}")
                    
                    st.error("❌ 建议：题库中已有相似题目，不建议重复添加")
                else:
                    st.success("✅ 未发现相似题目，可以添加到题库")
    
    # 处理添加
    if add_button:
        if not problem_text or not teacher_name:
            st.error("❌ 请至少填写题目内容和出题老师")
        else:
            # 查重（如果启用）
            should_add = True
            if check_duplicate:
                with st.spinner("🔍 查重中..."):
                    similar_problems = db.search_similar_problems(problem_text, limit=10)
                    
                    if similar_problems:
                        st.warning("⚠️ 发现可能相似的题目，请确认是否继续添加")
                        should_add = st.checkbox("确认添加（即使存在相似题目）", value=False)
            
            if should_add:
                with st.spinner("📝 正在添加到题库..."):
                    # 处理标签
                    tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else None
                    
                    # TODO: 这里可以添加质量审核和难度测试的逻辑
                    test_result = None
                    test_accuracy = None
                    quality_score = None
                    difficulty = None
                    
                    # 添加到数据库
                    problem_id = db.add_problem(
                        problem_text=problem_text,
                        teacher_name=teacher_name,
                        answer=answer if answer else None,
                        solution=solution if solution else None,
                        category=category,
                        test_model=None,
                        test_result=test_result,
                        test_accuracy=test_accuracy,
                        quality_score=quality_score,
                        originality_check=None,
                        difficulty=difficulty,
                        tags=tags
                    )
                    
                    if problem_id:
                        st.success(f"✅ 题目已成功添加到题库！")
                        st.info(f"题目 ID: {problem_id}")
                        
                        # 清空表单
                        st.rerun()
                    else:
                        st.error("❌ 添加失败，请检查数据库连接")

# ==================== 标签页 2：浏览题库 ====================
with tab2:
    st.markdown("### 📋 浏览题库")
    
    # 筛选条件
    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
    
    with col_filter1:
        filter_teacher = st.selectbox("筛选老师", ["全部"] + list(set([p.get('teacher_name') for p in db.get_all_problems(limit=1000) if p.get('teacher_name')])))
    
    with col_filter2:
        filter_category = st.selectbox("筛选类别", ["全部", "代数", "几何", "微积分", "概率统计", "数论", "其他"])
    
    with col_filter3:
        filter_difficulty = st.selectbox("筛选难度", ["全部", "简单", "中等", "困难"])
    
    with col_filter4:
        search_keyword = st.text_input("搜索关键词", placeholder="搜索题目内容...")
    
    # 获取题目列表
    problems = db.get_all_problems(
        teacher_name=filter_teacher if filter_teacher != "全部" else None,
        category=filter_category if filter_category != "全部" else None,
        difficulty=filter_difficulty if filter_difficulty != "全部" else None,
        limit=100
    )
    
    # 关键词搜索
    if search_keyword:
        problems = [p for p in problems if search_keyword.lower() in p['problem_text'].lower()]
    
    st.markdown(f"**共找到 {len(problems)} 道题目**")
    st.markdown("---")
    
    # 显示题目列表
    if not problems:
        st.info("📭 题库为空，请添加题目")
    else:
        for idx, problem in enumerate(problems, 1):
            with st.expander(f"题目 {idx} - {problem.get('category', 'Unknown')} - {problem.get('teacher_name', 'Unknown')}"):
                col_detail1, col_detail2 = st.columns([3, 1])
                
                with col_detail1:
                    st.markdown(f"**题目**: {problem['problem_text']}")
                    
                    if problem.get('answer'):
                        st.markdown(f"**答案**: {problem['answer']}")
                    
                    if problem.get('solution'):
                        st.markdown(f"**解析**: {problem['solution']}")
                
                with col_detail2:
                    st.markdown(f"**老师**: {problem.get('teacher_name', 'N/A')}")
                    st.markdown(f"**类别**: {problem.get('category', 'N/A')}")
                    st.markdown(f"**难度**: {problem.get('difficulty', 'N/A')}")
                    
                    if problem.get('test_accuracy'):
                        st.markdown(f"**Doubao正确率**: {problem['test_accuracy']}%")
                    
                    st.markdown(f"**添加时间**: {problem.get('created_at', 'N/A')[:10]}")
                    
                    # 操作按钮
                    if st.button("🗑️ 删除", key=f"del_{problem['id']}"):
                        if db.delete_problem(problem['id']):
                            st.success("✅ 已删除")
                            st.rerun()
                        else:
                            st.error("❌ 删除失败")

# ==================== 标签页 3：统计信息 ====================
with tab3:
    st.markdown("### 📊 题库统计")
    
    stats = db.get_statistics()
    
    # 总体统计
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.metric("📚 总题目数", stats.get('total_problems', 0))
    
    with col_stat2:
        st.metric("👨‍🏫 老师数量", len(stats.get('by_teacher', {})))
    
    with col_stat3:
        st.metric("🏷️ 类别数量", len(stats.get('by_category', {})))
    
    st.markdown("---")
    
    # 详细统计
    col_detail_stat1, col_detail_stat2 = st.columns(2)
    
    with col_detail_stat1:
        st.markdown("#### 按老师统计")
        by_teacher = stats.get('by_teacher', {})
        if by_teacher:
            for teacher, count in sorted(by_teacher.items(), key=lambda x: x[1], reverse=True):
                st.markdown(f"- **{teacher}**: {count} 道题")
        else:
            st.info("暂无数据")
    
    with col_detail_stat2:
        st.markdown("#### 按类别统计")
        by_category = stats.get('by_category', {})
        if by_category:
            for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
                st.markdown(f"- **{cat}**: {count} 道题")
        else:
            st.info("暂无数据")

