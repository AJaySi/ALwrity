-- Migration: Add user_websites table
-- Description: Stores automation metadata for generated websites

CREATE TABLE IF NOT EXISTS user_websites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL,
    github_repo_url VARCHAR(500),
    netlify_site_id VARCHAR(100),
    netlify_site_url VARCHAR(500),
    preview_url VARCHAR(500),
    template_type VARCHAR(50) NOT NULL DEFAULT 'blog',
    status VARCHAR(20) NOT NULL DEFAULT 'initializing',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_websites_user_id ON user_websites(user_id);

CREATE TRIGGER IF NOT EXISTS update_user_websites_timestamp 
    AFTER UPDATE ON user_websites
    FOR EACH ROW
BEGIN
    UPDATE user_websites 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;
