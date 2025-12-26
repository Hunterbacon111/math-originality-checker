"""
Supabase 数据库集成 - 题库管理系统
"""
import os
import hashlib
from datetime import datetime
from typing import Optional, List, Dict

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ supabase 包未安装，请运行: pip install supabase")

class Database:
    """数据库操作类"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.enabled = False
        self.client = None
        
        # 检查是否配置了 Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if supabase_url and supabase_key and SUPABASE_AVAILABLE:
            try:
                self.client: Client = create_client(supabase_url, supabase_key)
                self.enabled = True
                print("✅ Supabase 连接成功")
            except Exception as e:
                print(f"⚠️ Supabase 初始化失败: {e}")
    
    def _calculate_hash(self, text: str) -> str:
        """计算文本的 MD5 哈希值"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    # ==================== 题库管理功能 ====================
    
    def add_problem(
        self,
        problem_text: str,
        teacher_name: str,
        answer: Optional[str] = None,
        solution: Optional[str] = None,
        category: Optional[str] = None,
        test_model: Optional[str] = None,
        test_result: Optional[Dict] = None,
        test_accuracy: Optional[float] = None,
        quality_score: Optional[Dict] = None,
        originality_check: Optional[Dict] = None,
        difficulty: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        添加题目到题库
        
        Returns:
            str: 题目ID（成功）或 None（失败）
        """
        if not self.enabled:
            return None
        
        try:
            problem_hash = self._calculate_hash(problem_text)
            
            data = {
                "problem_text": problem_text,
                "teacher_name": teacher_name,
                "answer": answer,
                "solution": solution,
                "category": category,
                "test_model": test_model,
                "test_result": test_result,
                "test_accuracy": test_accuracy,
                "quality_score": quality_score,
                "originality_check": originality_check,
                "problem_hash": problem_hash,
                "difficulty": difficulty,
                "tags": tags
            }
            
            response = self.client.table("problems").insert(data).execute()
            
            if response.data:
                return response.data[0]['id']
            return None
            
        except Exception as e:
            print(f"❌ 添加题目失败: {e}")
            return None
    
    def get_all_problems(
        self,
        teacher_name: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        获取题库中的题目
        
        Args:
            teacher_name: 筛选老师
            category: 筛选类别
            difficulty: 筛选难度
            limit: 返回数量限制
        
        Returns:
            List[Dict]: 题目列表
        """
        if not self.enabled:
            return []
        
        try:
            query = self.client.table("problems").select("*").order("created_at", desc=True).limit(limit)
            
            if teacher_name:
                query = query.eq("teacher_name", teacher_name)
            if category:
                query = query.eq("category", category)
            if difficulty:
                query = query.eq("difficulty", difficulty)
            
            response = query.execute()
            return response.data
            
        except Exception as e:
            print(f"❌ 获取题目列表失败: {e}")
            return []
    
    def search_similar_problems(self, problem_text: str, limit: int = 30) -> List[Dict]:
        """
        搜索相似题目（用于查重）
        
        Args:
            problem_text: 新题目内容
            limit: 返回数量
        
        Returns:
            List[Dict]: 相似题目列表
        """
        if not self.enabled:
            return []
        
        try:
            # 先检查完全相同的题目（哈希匹配）
            problem_hash = self._calculate_hash(problem_text)
            exact_match = self.client.table("problems")\
                .select("*")\
                .eq("problem_hash", problem_hash)\
                .execute()
            
            if exact_match.data:
                return exact_match.data
            
            # 获取最近的题目用于智能对比
            response = self.client.table("problems")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            print(f"❌ 搜索相似题目失败: {e}")
            return []
    
    def get_problem_by_id(self, problem_id: str) -> Optional[Dict]:
        """根据ID获取题目详情"""
        if not self.enabled:
            return None
        
        try:
            response = self.client.table("problems")\
                .select("*")\
                .eq("id", problem_id)\
                .execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"❌ 获取题目详情失败: {e}")
            return None
    
    def update_problem(self, problem_id: str, updates: Dict) -> bool:
        """更新题目信息"""
        if not self.enabled:
            return False
        
        try:
            response = self.client.table("problems")\
                .update(updates)\
                .eq("id", problem_id)\
                .execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            print(f"❌ 更新题目失败: {e}")
            return False
    
    def delete_problem(self, problem_id: str) -> bool:
        """删除题目"""
        if not self.enabled:
            return False
        
        try:
            response = self.client.table("problems")\
                .delete()\
                .eq("id", problem_id)\
                .execute()
            
            return True
            
        except Exception as e:
            print(f"❌ 删除题目失败: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """获取题库统计信息"""
        if not self.enabled:
            return {
                "total_problems": 0,
                "by_teacher": {},
                "by_category": {},
                "by_difficulty": {}
            }
        
        try:
            # 总数
            all_problems = self.client.table("problems").select("*").execute()
            total = len(all_problems.data)
            
            # 按老师统计
            by_teacher = {}
            for p in all_problems.data:
                teacher = p.get('teacher_name', 'Unknown')
                by_teacher[teacher] = by_teacher.get(teacher, 0) + 1
            
            # 按类别统计
            by_category = {}
            for p in all_problems.data:
                cat = p.get('category', 'Uncategorized')
                by_category[cat] = by_category.get(cat, 0) + 1
            
            # 按难度统计
            by_difficulty = {}
            for p in all_problems.data:
                diff = p.get('difficulty', 'Unknown')
                by_difficulty[diff] = by_difficulty.get(diff, 0) + 1
            
            return {
                "total_problems": total,
                "by_teacher": by_teacher,
                "by_category": by_category,
                "by_difficulty": by_difficulty
            }
            
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {}


# 创建全局数据库实例
db = Database()


# 使用示例：
"""
from database import db

# 添加题目到题库
problem_id = db.add_problem(
    problem_text="求解方程 3x + 5 = 20",
    teacher_name="张老师",
    answer="x = 5",
    solution="移项得 3x = 15，两边除以3得 x = 5",
    category="代数",
    difficulty="简单",
    tags=["方程", "一元一次方程"]
)

# 查重检测
similar_problems = db.search_similar_problems("求解方程 3x + 5 = 20")

# 获取所有题目
all_problems = db.get_all_problems(limit=100)

# 按老师筛选
teacher_problems = db.get_all_problems(teacher_name="张老师")

# 获取统计信息
stats = db.get_statistics()

# 删除题目
db.delete_problem(problem_id)
"""

