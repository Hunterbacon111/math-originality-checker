#!/usr/bin/env python3
"""
使用 OpenAI GPT-5.1 对数学题目质量进行审核
模仿 test.py 的结构，简单稳定
只评判题目本身的质量，不验证答案正确性
"""
import json
import os
import time
import random
from openai import OpenAI

# ================= 配置区域 =================
# 1. 配置代理（使用测试成功的代理端口）
# 注释掉代理设置，直接连接 OpenAI API
# os.environ["http_proxy"] = "http://127.0.0.1:7897"
# os.environ["https_proxy"] = "http://127.0.0.1:7897"

# 2. OpenAI API Key - 从环境变量读取
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ 错误：未找到 OPENAI_API_KEY 环境变量")
    print("请在 .env 文件中配置或设置环境变量")
    exit(1)

# 3. 模型配置
MODEL_NAME = "gpt-5.1-chat-latest"  # 使用最新的 GPT-5.1

# 4. 筛选条件
CORRECT_COUNT_THRESHOLD = 4  # 审核正确次数≤4的题目

# 5. 文件路径
INPUT_FILE = "final_benchmark_results.jsonl"
ORIGINAL_PROBLEMS_FILE = "original_problems_only.json"
OUTPUT_FILE = "quality_review_results_gpt51.jsonl"
# ===========================================

client = OpenAI(api_key=api_key)

# 审核Prompt（专注题目质量，不评判答案正确性）
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

**Difficulty Level:** {difficulty}

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

def call_gpt_with_retry(prompt, model=MODEL_NAME):
    """
    带有重试机制的 API 调用函数（使用测试成功的API方式）
    解决 429 Rate Limit 问题
    """
    max_retries = 5
    base_wait_time = 10  # 基础等待时间 10秒

    for attempt in range(max_retries):
        try:
            # 发起请求（使用chat.completions.create，和测试脚本一样）
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}  # 强制返回JSON
            )
            return response.choices[0].message.content

        except Exception as e:
            error_str = str(e)
            # 检测是否是速率限制错误 (429)
            if "429" in error_str or "Rate limit" in error_str:
                # 计算等待时间：指数递增 + 随机抖动
                wait_time = (base_wait_time * (2 ** attempt)) + random.uniform(1, 5)
                print(f"  ⚠️  触发速率限制 (429)。休眠 {wait_time:.1f}秒后重试 ({attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                # 其他错误
                print(f"  ❌ API错误: {e}")
                return "API_ERROR"
    
    return "RATE_LIMIT_EXCEEDED"

def load_original_problems(filepath):
    """加载原始题目数据"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            problems = json.load(f)
            return {item['id']: item for item in problems}
    except FileNotFoundError:
        print(f"❌ 找不到文件: {filepath}")
        return {}

def main():
    print("=" * 80)
    print("🔍 数学题目质量审核系统 (OpenAI GPT-5.1)")
    print("=" * 80)
    print(f"模型: {MODEL_NAME}")
    print(f"代理: 127.0.0.1:7897")
    print(f"筛选条件: 正确次数 ≤ {CORRECT_COUNT_THRESHOLD}")
    print(f"评判标准: 只评估题目质量，不验证答案正确性")
    print("=" * 80)

    # 1. 加载原始题目
    print("\n📂 加载原始题目数据...")
    original_problems = load_original_problems(ORIGINAL_PROBLEMS_FILE)
    if not original_problems:
        return
    print(f"✅ 已加载 {len(original_problems)} 个原始题目")

    # 2. 加载需要审核的题目（正确次数≤4）
    print(f"\n📊 筛选需要审核的题目（正确次数 ≤ {CORRECT_COUNT_THRESHOLD}）...")
    problems_to_review = []
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get('correct_count', 999) <= CORRECT_COUNT_THRESHOLD:
                        problems_to_review.append(data)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"❌ 找不到文件: {INPUT_FILE}")
        return
    
    print(f"✅ 找到 {len(problems_to_review)} 个需要审核的题目")

    # 3. 断点续传：读取已处理的结果
    results = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        results.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            print(f"📖 检测到已有进度，已完成 {len(results)} 题")
        except:
            results = []

    # 获取已处理 ID 集合
    processed_ids = {item['id'] for item in results if 'id' in item}

    # 4. 确认是否继续
    remaining = len(problems_to_review) - len(processed_ids)
    print(f"\n待审核题目: {remaining} 题")
    
    if remaining == 0:
        print("✅ 所有题目已审核完成！")
        return
    
    # 预估成本（GPT-4o: $2.5/1M input + $10/1M output）
    estimated_cost = remaining * 800 / 1_000_000 * 6.25  # 粗略估计
    print(f"⚠️  预计成本: ~${estimated_cost:.2f} USD")
    
    response = input(f"\n是否继续审核 {remaining} 个题目？(y/n): ")
    if response.lower() != 'y':
        print("❌ 已取消")
        return

    # 5. 开始审核
    print(f"\n🚀 开始审核...")
    print("=" * 80)

    success_count = 0
    error_count = 0

    for idx, problem_data in enumerate(problems_to_review):
        problem_id = problem_data['id']
        
        # 跳过已处理的
        if problem_id in processed_ids:
            continue

        # 获取原始题目文本
        original = original_problems.get(problem_id, {})
        problem_text = original.get('problem_text', '')
        
        if not problem_text:
            print(f"⚠️  [{idx+1}/{len(problems_to_review)}] 题目 {problem_id} 缺少文本，跳过")
            continue

        print(f"\n🔍 [{idx+1}/{len(problems_to_review)}] 审核题目 ID: {problem_id}")
        
        # 构造 Prompt
        prompt = REVIEW_PROMPT_TEMPLATE.format(
            problem_text=problem_text,
            difficulty=problem_data.get('difficulty', 'Unknown')
        )
        
        # 调用 API
        analysis = call_gpt_with_retry(prompt)
        
        # 处理失败情况
        if analysis == "RATE_LIMIT_EXCEEDED":
            print("🚫 多次重试失败，程序停止")
            break
        
        if analysis == "API_ERROR":
            error_count += 1
            # 记录错误但继续
            result_entry = {
                'id': problem_id,
                'difficulty': problem_data.get('difficulty', 'Unknown'),
                'correct_count': problem_data.get('correct_count', 0),
                'pass_rate': problem_data.get('pass_rate', ''),
                'ground_truth': problem_data.get('ground_truth', ''),
                'review': {
                    'total_score': 0,
                    'issues': ['API call failed'],
                    'reasoning': 'System error',
                    'recommendation': 'ERROR'
                }
            }
        else:
            # 解析JSON
            try:
                review_result = json.loads(analysis)
                success_count += 1
                
                # 打印结果
                score = review_result.get('total_score', 0)
                recommendation = review_result.get('recommendation', 'UNKNOWN')
                
                if 'ACCEPT' in recommendation:
                    status = "✅"
                elif 'BORDERLINE' in recommendation:
                    status = "⚠️"
                else:
                    status = "❌"
                
                print(f"  {status} 评分: {score}/10 | {recommendation}")
                
                result_entry = {
                    'id': problem_id,
                    'difficulty': problem_data.get('difficulty', 'Unknown'),
                    'correct_count': problem_data.get('correct_count', 0),
                    'pass_rate': problem_data.get('pass_rate', ''),
                    'ground_truth': problem_data.get('ground_truth', ''),
                    'review': review_result
                }
                
            except json.JSONDecodeError:
                error_count += 1
                print(f"  ⚠️  JSON解析失败")
                result_entry = {
                    'id': problem_id,
                    'difficulty': problem_data.get('difficulty', 'Unknown'),
                    'correct_count': problem_data.get('correct_count', 0),
                    'review': {
                        'total_score': 0,
                        'issues': ['Failed to parse JSON'],
                        'reasoning': analysis[:200],
                        'recommendation': 'ERROR'
                    }
                }
        
        # 实时保存（追加到文件）
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(result_entry, ensure_ascii=False) + '\n')
        
        # 主动休眠，避免频繁调用
        time.sleep(2)

    # 6. 完成统计
    print("\n" + "=" * 80)
    print("📊 审核完成")
    print("=" * 80)
    print(f"✅ 成功: {success_count} 题")
    print(f"❌ 失败: {error_count} 题")
    print(f"💾 结果已保存至: {OUTPUT_FILE}")
    print("=" * 80)
    print("\n🎯 下一步: python3 analyze_review_gemini3.py")

if __name__ == "__main__":
    main()

