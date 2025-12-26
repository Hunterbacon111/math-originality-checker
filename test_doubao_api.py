#!/usr/bin/env python3
"""
测试豆包 API 连接和权限
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 豆包配置
DOUBAO_API_KEY_1 = os.getenv("DOUBAO_API_KEY_1")
DOUBAO_API_KEY_2 = os.getenv("DOUBAO_API_KEY_2")
DOUBAO_MODEL_1 = "ep-m-20251211112628-2r5n6"
DOUBAO_MODEL_2 = "ep-m-20251225141150-hfztd"
DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

def test_doubao_api(api_key, model_id, name):
    """测试单个豆包 API"""
    print(f"\n{'='*60}")
    print(f"测试 {name}")
    print(f"{'='*60}")
    print(f"API Key: {api_key[:20]}...{api_key[-10:] if api_key else 'None'}")
    print(f"端点 ID: {model_id}")
    print(f"Base URL: {DOUBAO_BASE_URL}")
    
    if not api_key:
        print(f"❌ {name} 未配置 API Key")
        return False
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=DOUBAO_BASE_URL
        )
        
        print("\n发送测试请求...")
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "user",
                    "content": "请计算 2 + 2 = ?"
                }
            ],
            stream=False
        )
        
        result = response.choices[0].message.content
        print(f"✅ {name} 连接成功！")
        print(f"模型响应: {result[:100]}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ {name} 连接失败！")
        print(f"错误信息: {error_msg}")
        
        # 详细诊断
        if "403" in error_msg or "AccessDenied" in error_msg:
            print("\n🔍 诊断: 403 AccessDenied 错误")
            print("可能原因:")
            print("  1. API Key 没有权限访问该端点")
            print("  2. API Key 已失效或被吊销")
            print("  3. 端点 ID 不正确")
            print("  4. 账户欠费或超过配额")
            print("\n💡 解决方案:")
            print("  - 检查火山引擎控制台的 API Key 权限")
            print("  - 确认端点 ID 是否正确")
            print("  - 检查账户余额")
            print("  - 尝试重新创建 API Key")
            
        elif "404" in error_msg:
            print("\n🔍 诊断: 404 Not Found 错误")
            print("可能原因:")
            print("  1. 端点 ID 不存在或已删除")
            print("  2. Base URL 不正确")
            print("\n💡 解决方案:")
            print("  - 在火山引擎控制台确认端点 ID")
            
        elif "429" in error_msg:
            print("\n🔍 诊断: 429 Too Many Requests 错误")
            print("可能原因:")
            print("  1. 请求频率超过限制")
            print("  2. 并发数超过限制")
            print("\n💡 解决方案:")
            print("  - 稍等片刻后重试")
            print("  - 减少并发请求数")
            
        return False

def main():
    print("\n" + "="*60)
    print("🚀 豆包 API 诊断工具")
    print("="*60)
    
    # 测试豆包一号
    success_1 = test_doubao_api(DOUBAO_API_KEY_1, DOUBAO_MODEL_1, "Doubao 一号")
    
    # 测试豆包二号
    success_2 = test_doubao_api(DOUBAO_API_KEY_2, DOUBAO_MODEL_2, "Doubao 二号")
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"Doubao 一号: {'✅ 正常' if success_1 else '❌ 异常'}")
    print(f"Doubao 二号: {'✅ 正常' if success_2 else '❌ 异常'}")
    
    if not success_1 and not success_2:
        print("\n⚠️ 所有 API 都无法使用！")
        print("建议:")
        print("  1. 登录火山引擎控制台: https://console.volcengine.com/ark")
        print("  2. 检查 API Key 状态")
        print("  3. 确认端点 ID")
        print("  4. 检查账户余额")
    elif not success_1:
        print("\n💡 建议: 使用 Doubao 二号")
    elif not success_2:
        print("\n💡 建议: 使用 Doubao 一号")
    else:
        print("\n✅ 所有 API 都可以正常使用！")

if __name__ == "__main__":
    main()

