-- Blog Writer Task Persistence Tables
-- Creates tables for storing task state, progress, and metrics

-- Tasks table - stores main task information
CREATE TABLE IF NOT EXISTS blog_writer_tasks (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    task_type VARCHAR(50) NOT NULL, -- 'research', 'outline', 'content', 'seo', 'medium_generation'
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    request_data JSONB, -- Original request parameters
    result_data JSONB, -- Final result data
    error_data JSONB, -- Error information if failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    correlation_id VARCHAR(36), -- For request tracing
    operation VARCHAR(100), -- Specific operation being performed
    retry_count INTEGER DEFAULT 0, -- Number of retry attempts
    max_retries INTEGER DEFAULT 3, -- Maximum retry attempts allowed
    priority INTEGER DEFAULT 0, -- Task priority (higher = more important)
    metadata JSONB -- Additional metadata
);

-- Task progress table - stores progress updates
CREATE TABLE IF NOT EXISTS blog_writer_task_progress (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL REFERENCES blog_writer_tasks(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message TEXT NOT NULL,
    percentage DECIMAL(5,2) DEFAULT 0.00, -- 0.00 to 100.00
    progress_type VARCHAR(50) DEFAULT 'info', -- 'info', 'warning', 'error', 'success'
    metadata JSONB -- Additional progress metadata
);

-- Task metrics table - stores performance metrics
CREATE TABLE IF NOT EXISTS blog_writer_task_metrics (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL REFERENCES blog_writer_tasks(id) ON DELETE CASCADE,
    operation VARCHAR(100) NOT NULL,
    duration_ms INTEGER NOT NULL,
    token_usage JSONB, -- Token usage statistics
    api_calls INTEGER DEFAULT 0,
    cache_hits INTEGER DEFAULT 0,
    cache_misses INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB -- Additional metrics
);

-- Task recovery table - stores recovery information
CREATE TABLE IF NOT EXISTS blog_writer_task_recovery (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(36) NOT NULL REFERENCES blog_writer_tasks(id) ON DELETE CASCADE,
    recovery_reason VARCHAR(100) NOT NULL, -- 'server_restart', 'timeout', 'error'
    recovery_action VARCHAR(100) NOT NULL, -- 'resume', 'retry', 'fail'
    checkpoint_data JSONB, -- State at recovery point
    recovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    recovery_successful BOOLEAN DEFAULT FALSE,
    metadata JSONB
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_blog_writer_tasks_user_id ON blog_writer_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_blog_writer_tasks_status ON blog_writer_tasks(status);
CREATE INDEX IF NOT EXISTS idx_blog_writer_tasks_created_at ON blog_writer_tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_blog_writer_tasks_task_type ON blog_writer_tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_blog_writer_tasks_correlation_id ON blog_writer_tasks(correlation_id);

CREATE INDEX IF NOT EXISTS idx_blog_writer_task_progress_task_id ON blog_writer_task_progress(task_id);
CREATE INDEX IF NOT EXISTS idx_blog_writer_task_progress_timestamp ON blog_writer_task_progress(timestamp);

CREATE INDEX IF NOT EXISTS idx_blog_writer_task_metrics_task_id ON blog_writer_task_metrics(task_id);
CREATE INDEX IF NOT EXISTS idx_blog_writer_task_metrics_operation ON blog_writer_task_metrics(operation);
CREATE INDEX IF NOT EXISTS idx_blog_writer_task_metrics_created_at ON blog_writer_task_metrics(created_at);

CREATE INDEX IF NOT EXISTS idx_blog_writer_task_recovery_task_id ON blog_writer_task_recovery(task_id);
CREATE INDEX IF NOT EXISTS idx_blog_writer_task_recovery_recovered_at ON blog_writer_task_recovery(recovered_at);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_blog_writer_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_blog_writer_tasks_updated_at
    BEFORE UPDATE ON blog_writer_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_blog_writer_tasks_updated_at();

-- Function to clean up old completed tasks (older than 7 days)
CREATE OR REPLACE FUNCTION cleanup_old_blog_writer_tasks()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM blog_writer_tasks 
    WHERE status IN ('completed', 'failed', 'cancelled') 
    AND created_at < NOW() - INTERVAL '7 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ language 'plpgsql';

-- Create a view for task analytics
CREATE OR REPLACE VIEW blog_writer_task_analytics AS
SELECT 
    task_type,
    status,
    COUNT(*) as task_count,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_duration_seconds,
    AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_processing_time_seconds,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count,
    COUNT(CASE WHEN status = 'running' THEN 1 END) as running_count,
    ROUND(
        COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*), 
        2
    ) as success_rate_percentage
FROM blog_writer_tasks
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY task_type, status
ORDER BY task_type, status;

-- Create a view for performance metrics
CREATE OR REPLACE VIEW blog_writer_performance_metrics AS
SELECT 
    t.task_type,
    t.operation,
    COUNT(m.id) as metric_count,
    AVG(m.duration_ms) as avg_duration_ms,
    MIN(m.duration_ms) as min_duration_ms,
    MAX(m.duration_ms) as max_duration_ms,
    SUM(m.api_calls) as total_api_calls,
    SUM(m.cache_hits) as total_cache_hits,
    SUM(m.cache_misses) as total_cache_misses,
    ROUND(
        SUM(m.cache_hits) * 100.0 / NULLIF(SUM(m.cache_hits + m.cache_misses), 0), 
        2
    ) as cache_hit_rate_percentage
FROM blog_writer_tasks t
LEFT JOIN blog_writer_task_metrics m ON t.id = m.task_id
WHERE t.created_at >= NOW() - INTERVAL '7 days'
GROUP BY t.task_type, t.operation
ORDER BY t.task_type, t.operation;
