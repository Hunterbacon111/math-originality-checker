#!/usr/bin/env python3
"""
测试 Supabase 连接
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def test_supabase_connection():
    """测试 Supabase 数据库连接"""
    print("\n" + "="*60)
    print("🧪 测试 Supabase 连接")
    print("="*60)
    
    # 获取环境变量
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ 未配置 Supabase 环境变量")
        print("\n请在 .env 文件中添加：")
        print("  SUPABASE_URL=your-project-url")
        print("  SUPABASE_KEY=your-anon-key")
        return False
    
    print(f"📋 URL: {url[:30]}...")
    print(f"🔑 Key: {key[:30]}...")
    
    try:
        # 创建客户端
        supabase: Client = create_client(url, key)
        print("\n✅ Supabase 客户端创建成功")
        
        # 测试查询
        print("\n🔍 测试查询 problems 表...")
        response = supabase.table('problems').select("*").limit(1).execute()
        
        print(f"✅ 查询成功！当前题库数量: {len(response.data)}")
        
        if len(response.data) > 0:
            print("\n📊 示例数据:")
            print(f"  ID: {response.data[0].get('id')}")
            print(f"  老师: {response.data[0].get('teacher_name', 'N/A')}")
            print(f"  类别: {response.data[0].get('category', 'N/A')}")
        else:
            print("\n💡 题库为空，可以开始添加题目了！")
        
        print("\n" + "="*60)
        print("✅ Supabase 连接测试通过！")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n🔍 可能的原因：")
        print("  1. SUPABASE_URL 或 SUPABASE_KEY 不正确")
        print("  2. problems 表尚未创建（请运行 SQL 脚本）")
        print("  3. 网络连接问题")
        return False

if __name__ == "__main__":
    test_supabase_connection()

