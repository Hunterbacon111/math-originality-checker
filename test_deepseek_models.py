#!/usr/bin/env python3
"""
测试 DeepSeek 不同模型标识符
"""
import os
from openai import OpenAI

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-68a64c7599774791aad04ff5043c5806")

# 可能的模型名称列表
models_to_test = [
    "deepseek-chat",
    "deepseek-v3",
    "deepseek-v3-chat",
    "deepseek-v3-base",
]

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

print("=" * 70)
print("🧪 测试不同的 DeepSeek 模型标识符")
print("=" * 70)

for model_name in models_to_test:
    print(f"\n📡 测试模型: {model_name}")
    print("-" * 70)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "你好，请简短回答：你是什么模型？版本是什么？"}
            ],
            max_tokens=50
        )
        
        actual_model = response.model
        reply = response.choices[0].message.content
        
        print(f"✅ 成功！")
        print(f"   返回的模型: {actual_model}")
        print(f"   模型回答: {reply}")
        
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg or "not found" in error_msg:
            print(f"❌ 模型不存在")
        else:
            print(f"❌ 错误: {error_msg[:100]}")

print("\n" + "=" * 70)
print("💡 结论：使用测试成功的模型标识符")
print("=" * 70)

