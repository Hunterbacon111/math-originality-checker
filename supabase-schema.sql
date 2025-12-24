-- =============================================
-- 数学题目审核系统 - Supabase 数据库架构
-- =============================================

-- 1. 审核记录表
CREATE TABLE IF NOT EXISTS problem_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    problem_text TEXT NOT NULL,
    review_type TEXT CHECK (review_type IN ('quality', 'originality')),
    result JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 创建索引以提升查询性能
CREATE INDEX IF NOT EXISTS idx_reviews_created 
    ON problem_reviews(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_reviews_type 
    ON problem_reviews(review_type);

CREATE INDEX IF NOT EXISTS idx_reviews_user 
    ON problem_reviews(user_id);

-- 3. 创建全文搜索索引（用于搜索题目内容）
CREATE INDEX IF NOT EXISTS idx_reviews_problem_text 
    ON problem_reviews USING GIN (to_tsvector('simple', problem_text));

-- 4. 添加注释
COMMENT ON TABLE problem_reviews IS '数学题目审核记录表';
COMMENT ON COLUMN problem_reviews.id IS '记录唯一标识';
COMMENT ON COLUMN problem_reviews.user_id IS '用户ID（可选）';
COMMENT ON COLUMN problem_reviews.problem_text IS '题目内容';
COMMENT ON COLUMN problem_reviews.review_type IS '审核类型：quality=质量审核，originality=原创度检测';
COMMENT ON COLUMN problem_reviews.result IS '审核结果JSON数据';
COMMENT ON COLUMN problem_reviews.created_at IS '创建时间';

-- 5. 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_problem_reviews_updated_at 
    BEFORE UPDATE ON problem_reviews 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 6. 创建视图：最近的审核统计
CREATE OR REPLACE VIEW review_stats AS
SELECT 
    COUNT(*) as total_reviews,
    COUNT(*) FILTER (WHERE review_type = 'quality') as quality_reviews,
    COUNT(*) FILTER (WHERE review_type = 'originality') as originality_reviews,
    COUNT(DISTINCT DATE(created_at)) as active_days,
    MAX(created_at) as last_review_time
FROM problem_reviews;

-- 7. 创建视图：每日审核统计
CREATE OR REPLACE VIEW daily_review_stats AS
SELECT 
    DATE(created_at) as review_date,
    COUNT(*) as total_count,
    COUNT(*) FILTER (WHERE review_type = 'quality') as quality_count,
    COUNT(*) FILTER (WHERE review_type = 'originality') as originality_count
FROM problem_reviews
GROUP BY DATE(created_at)
ORDER BY review_date DESC;

-- 8. Row Level Security (RLS) 策略（可选）
-- 如果需要用户认证和权限控制，启用 RLS

-- ALTER TABLE problem_reviews ENABLE ROW LEVEL SECURITY;

-- 允许所有人插入（如果是公开应用）
-- CREATE POLICY "Allow insert for all" ON problem_reviews
--     FOR INSERT WITH CHECK (true);

-- 允许用户查看自己的记录
-- CREATE POLICY "Users can view own records" ON problem_reviews
--     FOR SELECT USING (auth.uid() = user_id);

-- 9. 示例查询

-- 查询最近 10 条审核记录
-- SELECT * FROM problem_reviews 
-- ORDER BY created_at DESC 
-- LIMIT 10;

-- 查询特定类型的审核记录
-- SELECT * FROM problem_reviews 
-- WHERE review_type = 'quality'
-- ORDER BY created_at DESC;

-- 查询统计信息
-- SELECT * FROM review_stats;

-- 搜索包含特定关键词的题目
-- SELECT * FROM problem_reviews 
-- WHERE to_tsvector('simple', problem_text) @@ to_tsquery('simple', '微积分');

-- =============================================
-- 使用说明：
-- 1. 在 Supabase 控制台的 SQL Editor 中运行此脚本
-- 2. 脚本会创建必要的表、索引和视图
-- 3. 如需用户认证，取消 RLS 相关注释
-- =============================================

