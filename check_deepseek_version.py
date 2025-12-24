#!/usr/bin/env python3
"""
检查 DeepSeek 模型版本
"""
import os
from openai import OpenAI

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-68a64c7599774791aad04ff5043c5806")

print("=" * 60)
print("🔍 DeepSeek 模型版本检查")
print("=" * 60)

try:
    # 创建客户端
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )
    
    # 测试调用
    print("\n📡 正在测试 DeepSeek API...")
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": "请告诉我你的模型版本号，只回答版本号即可。"}
        ],
        max_tokens=100
    )
    
    version_info = response.choices[0].message.content
    model_used = response.model  # API 返回的实际模型名称
    
    print("\n✅ 连接成功！")
    print(f"\n📊 使用的模型标识符: deepseek-chat")
    print(f"📊 API 返回的实际模型: {model_used}")
    print(f"📊 模型自述版本: {version_info}")
    
    # 检查是否为 V3
    if "v3" in version_info.lower() or "v3" in model_used.lower():
        print("\n🎉 确认：正在使用 DeepSeek V3（最新版本）")
    else:
        print(f"\n⚠️  检测到的版本: {version_info}")
        print("建议访问 https://platform.deepseek.com/docs 确认最新版本")
    
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    print("\n可能的原因:")
    print("1. API Key 无效或过期")
    print("2. 网络连接问题")
    print("3. API 配额用完")
    print("\n请访问 https://platform.deepseek.com 检查账户状态")

print("\n💡 提示:")
print("- deepseek-chat 会自动指向最新的稳定版本")
print("- 当前最新版本是 DeepSeek-V3 (2025年1月发布)")
print("- 如果需要指定版本，请查看官方文档")

