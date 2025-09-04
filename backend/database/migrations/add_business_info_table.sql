-- Migration: Add user_business_info table
-- Description: Creates table for storing business information when users don't have websites
-- Date: 2024-01-XX

CREATE TABLE IF NOT EXISTS user_business_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    business_description TEXT NOT NULL,
    industry VARCHAR(100),
    target_audience TEXT,
    business_goals TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster user lookups
CREATE INDEX IF NOT EXISTS idx_user_business_info_user_id ON user_business_info(user_id);

-- Add trigger to automatically update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_user_business_info_timestamp 
    AFTER UPDATE ON user_business_info
    FOR EACH ROW
BEGIN
    UPDATE user_business_info 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;
