#!/usr/bin/env python3
"""
批量导入题目到数据库
"""
import json
import sys
from database import db
from dotenv import load_dotenv

load_dotenv()

def import_problems_from_json(json_file_path, teacher_name="导入", category="未分类"):
    """
    从 JSON 文件批量导入题目
    
    Args:
        json_file_path: JSON 文件路径
        teacher_name: 默认出题老师名称
        category: 默认类别
    """
    
    if not db.enabled:
        print("❌ 数据库未连接，请检查 Supabase 配置")
        return
    
    print(f"\n{'='*60}")
    print(f"📚 批量导入题目工具")
    print(f"{'='*60}\n")
    
    # 读取 JSON 文件
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            # 尝试读取为 JSON 数组
            content = f.read().strip()
            
            # 支持两种格式：JSON 数组 或 JSONL（每行一个 JSON）
            if content.startswith('['):
                problems_data = json.loads(content)
            else:
                # JSONL 格式
                problems_data = [json.loads(line) for line in content.split('\n') if line.strip()]
        
        print(f"✅ 成功读取文件: {json_file_path}")
        print(f"📊 共找到 {len(problems_data)} 道题目\n")
    
    except FileNotFoundError:
        print(f"❌ 文件不存在: {json_file_path}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式错误: {e}")
        return
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    # 显示数据格式示例
    if problems_data:
        print("📋 数据格式示例（第一题）:")
        first_problem = problems_data[0]
        print(f"  可用字段: {list(first_problem.keys())}")
        print()
    
    # 询问字段映射
    print("🔧 字段映射配置")
    print("请告诉我 JSON 中各字段对应的键名（如果没有该字段，直接按回车跳过）:\n")
    
    field_mapping = {}
    field_mapping['problem_text'] = input(f"题目内容的字段名 [{', '.join([k for k in first_problem.keys() if 'problem' in k.lower() or 'question' in k.lower() or 'text' in k.lower()][:3])}]: ").strip()
    field_mapping['answer'] = input(f"答案的字段名 [{', '.join([k for k in first_problem.keys() if 'answer' in k.lower()][:3])}]: ").strip()
    field_mapping['solution'] = input(f"解析的字段名 [{', '.join([k for k in first_problem.keys() if 'solution' in k.lower() or 'explanation' in k.lower()][:3])}]: ").strip()
    field_mapping['id'] = input(f"题目ID的字段名 [{', '.join([k for k in first_problem.keys() if 'id' in k.lower()][:3])}]: ").strip()
    
    # 可选字段
    print("\n可选字段（可以直接按回车跳过）:")
    field_mapping['difficulty'] = input("难度字段名: ").strip()
    field_mapping['tags'] = input("标签字段名: ").strip()
    
    print()
    
    # 如果字段为空，尝试自动检测
    if not field_mapping['problem_text']:
        for key in ['problem', 'question', 'problem_text', 'text', 'content']:
            if key in first_problem:
                field_mapping['problem_text'] = key
                print(f"✅ 自动检测到题目字段: {key}")
                break
    
    if not field_mapping['answer']:
        for key in ['answer', 'solution', 'result']:
            if key in first_problem:
                field_mapping['answer'] = key
                print(f"✅ 自动检测到答案字段: {key}")
                break
    
    if not field_mapping['solution']:
        for key in ['explanation', 'solution', 'analysis', '解析']:
            if key in first_problem:
                field_mapping['solution'] = key
                print(f"✅ 自动检测到解析字段: {key}")
                break
    
    # 确认必填字段
    if not field_mapping['problem_text']:
        print("\n❌ 错误：必须指定题目内容字段")
        return
    
    # 询问默认值
    print(f"\n📝 默认值设置:")
    teacher_name = input(f"出题老师名称 [默认: {teacher_name}]: ").strip() or teacher_name
    category = input(f"题目类别 [默认: {category}]: ").strip() or category
    
    # 确认导入
    print(f"\n{'='*60}")
    print("📋 导入配置确认:")
    print(f"  • 题目数量: {len(problems_data)}")
    print(f"  • 出题老师: {teacher_name}")
    print(f"  • 默认类别: {category}")
    print(f"  • 题目字段: {field_mapping['problem_text']}")
    print(f"  • 答案字段: {field_mapping.get('answer', '无')}")
    print(f"  • 解析字段: {field_mapping.get('solution', '无')}")
    print(f"{'='*60}\n")
    
    confirm = input("确认开始导入？(y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 已取消导入")
        return
    
    # 开始导入
    print(f"\n{'='*60}")
    print("🚀 开始导入...")
    print(f"{'='*60}\n")
    
    success_count = 0
    error_count = 0
    
    for idx, problem_data in enumerate(problems_data, 1):
        try:
            # 提取数据
            problem_text = problem_data.get(field_mapping['problem_text'], '')
            
            if not problem_text:
                print(f"⚠️  题目 {idx}: 跳过（题目内容为空）")
                error_count += 1
                continue
            
            answer = problem_data.get(field_mapping.get('answer', ''), None) if field_mapping.get('answer') else None
            solution = problem_data.get(field_mapping.get('solution', ''), None) if field_mapping.get('solution') else None
            difficulty = problem_data.get(field_mapping.get('difficulty', ''), None) if field_mapping.get('difficulty') else None
            
            # 处理标签
            tags = None
            if field_mapping.get('tags'):
                tags_data = problem_data.get(field_mapping['tags'])
                if isinstance(tags_data, list):
                    tags = tags_data
                elif isinstance(tags_data, str):
                    tags = [tags_data]
            
            # 添加到数据库
            problem_id = db.add_problem(
                problem_text=problem_text,
                teacher_name=teacher_name,
                answer=answer,
                solution=solution,
                category=category,
                difficulty=difficulty,
                tags=tags
            )
            
            if problem_id:
                print(f"✅ 题目 {idx}/{len(problems_data)}: 导入成功 (ID: {problem_id[:8]}...)")
                success_count += 1
            else:
                print(f"❌ 题目 {idx}/{len(problems_data)}: 导入失败")
                error_count += 1
        
        except Exception as e:
            print(f"❌ 题目 {idx}/{len(problems_data)}: 导入失败 - {e}")
            error_count += 1
    
    # 导入总结
    print(f"\n{'='*60}")
    print("📊 导入完成！")
    print(f"{'='*60}")
    print(f"✅ 成功: {success_count} 道题目")
    print(f"❌ 失败: {error_count} 道题目")
    print(f"📈 成功率: {success_count/len(problems_data)*100:.1f}%")
    print(f"{'='*60}\n")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
📚 批量导入题目工具

使用方法:
    python batch_import_problems.py <json_file_path> [teacher_name] [category]

参数说明:
    json_file_path  - JSON 文件路径（必需）
    teacher_name    - 出题老师名称（可选，默认: "导入"）
    category        - 题目类别（可选，默认: "未分类"）

示例:
    python batch_import_problems.py problems.json "张老师" "代数"
    python batch_import_problems.py problems.jsonl
        """)
        return
    
    json_file = sys.argv[1]
    teacher_name = sys.argv[2] if len(sys.argv) > 2 else "导入"
    category = sys.argv[3] if len(sys.argv) > 3 else "未分类"
    
    import_problems_from_json(json_file, teacher_name, category)

if __name__ == "__main__":
    main()

