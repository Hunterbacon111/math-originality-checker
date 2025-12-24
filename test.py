import json
import os
import time
import random
from openai import OpenAI

# ================= 配置区域 =================
# 1. 配置代理
os.environ["http_proxy"] = "http://127.0.0.1:17890"
os.environ["https_proxy"] = "http://127.0.0.1:17890"

# 2. API Key - 从环境变量读取
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ 错误：未找到 OPENAI_API_KEY 环境变量")
    print("请在 .env 文件中配置或设置环境变量")
    exit(1) 

# 3. 文件路径
input_file = "dataset_fixed.json"      # 你的源数据文件
output_file = "originality_report.json" # 结果保存文件
# ===========================================

client = OpenAI(api_key=api_key)

def load_json_data(filepath):
    """
    智能读取 JSON 数据，兼容列表或字典格式
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 如果数据直接是列表 [{}, {}]
        if isinstance(data, list):
            return data
        
        # 如果数据是字典 {"fullContent": [...]}
        elif isinstance(data, dict):
            if "fullContent" in data:
                return data["fullContent"]
            # 尝试寻找字典中第一个是列表的值
            for key, val in data.items():
                if isinstance(val, list):
                    return val
        
        print("❌ 错误：无法解析 JSON 结构，请检查文件格式。")
        return []
    except FileNotFoundError:
        print(f"❌ 找不到文件: {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"❌ JSON 文件格式错误")
        return []

def call_gpt_with_retry(prompt, model="gpt-5.1-chat-latest"):
    """
    带有重试机制的 API 调用函数
    解决 429 Rate Limit 问题
    """
    max_retries = 5
    base_wait_time = 10  # 基础等待时间 10秒

    for attempt in range(max_retries):
        try:
            # 发起请求
            response = client.responses.create(
                model=model,
                tools=[{"type": "web_search"}],
                input=prompt
            )
            return response.output_text

        except Exception as e:
            error_str = str(e)
            # 检测是否是速率限制错误 (429)
            if "429" in error_str or "Rate limit" in error_str:
                # 计算等待时间：指数递增 (10s -> 20s -> 40s...) + 随机抖动防止并发冲突
                wait_time = (base_wait_time * (2 ** attempt)) + random.uniform(1, 5)
                print(f"\n⚠️ 触发速率限制 (429)。正在休眠 {wait_time:.1f} 秒后重试 (尝试 {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                # 如果是其他错误（如网络断开），打印并返回错误
                print(f"\n❌ API 未知错误: {e}")
                return "API_ERROR"
    
    return "RATE_LIMIT_EXCEEDED"

def main():
    # 1. 读取题目
    problems = load_json_data(input_file)
    if not problems:
        return

    print(f"✅ 成功加载 {len(problems)} 道题目。")

    # 2. 断点续传：读取已处理的结果
    results = []
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
                print(f"📖 检测到已有进度，已跳过前 {len(results)} 条记录。")
        except:
            results = []

    # 获取已处理 ID 集合，防止重复跑
    processed_ids = {item['id'] for item in results if 'id' in item}

    # 3. 基础 Prompt
    base_prompt = """
    Don't solve this problem, just search if there are similar problems in the website. 
    Try to understand the core of the problem and don't just focus on syntax.
    
    After searching, please explicitly state:
    1. "STATUS: DUPLICATE" if you found the same or very similar problem (provide the Source URL).
    2. "STATUS: ORIGINAL" if you found nothing similar.
    3. Provide a brief summary of what you found.
    
    Here is the problem content:
    """

    # 4. 循环处理
    for idx, item in enumerate(problems):
        # 获取 ID，如果没有 ID 则用索引代替
        p_id = item.get('id', f"unknown_{idx}")
        
        # 跳过已处理的
        if p_id in processed_ids:
            continue

        p_text = item.get('problem_text', '')
        if not p_text:
            print(f"⚠️ 跳过空题目 ID: {p_id}")
            continue

        print(f"🔍 [{idx+1}/{len(problems)}] 正在搜索题目 ID: {p_id} ...")
        
        # 构造完整 Query
        full_query = base_prompt + f"\n\n{p_text}"
        
        # === 调用 API (含重试机制) ===
        analysis = call_gpt_with_retry(full_query)
        
        # 如果多次重试失败，停止脚本防止浪费
        if analysis == "RATE_LIMIT_EXCEEDED":
            print("🚫 错误：多次重试失败，程序停止。请稍后再试。")
            break

        # 简单判断结果
        is_original = "STATUS: ORIGINAL" in analysis
        
        # 记录数据
        result_entry = {
            "id": p_id,
            "problem_text_preview": p_text[:50] + "...", 
            "is_original_guess": is_original,
            "gpt_analysis": analysis
        }
        results.append(result_entry)

        # 5. 实时保存 (每做完一条就存一次，防止程序中断数据丢失)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        
        # 6. 主动休眠：虽然有重试机制，但平时也稍微慢一点，建议 3~5 秒
        time.sleep(3) 

    print(f"\n🎉 任务结束！结果已保存至 {output_file}")

if __name__ == "__main__":
    main()

    