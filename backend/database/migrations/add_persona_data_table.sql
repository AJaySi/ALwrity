-- Migration: Add persona_data table for onboarding step 4
-- Created: 2025-10-10
-- Description: Adds table to store persona generation data from onboarding step 4

CREATE TABLE IF NOT EXISTS persona_data (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    core_persona JSONB,
    platform_personas JSONB,
    quality_metrics JSONB,
    selected_platforms JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES onboarding_sessions(id) ON DELETE CASCADE
);

-- Add index for better query performance
CREATE INDEX IF NOT EXISTS idx_persona_data_session_id ON persona_data(session_id);
CREATE INDEX IF NOT EXISTS idx_persona_data_created_at ON persona_data(created_at);

-- Add comment to table
COMMENT ON TABLE persona_data IS 'Stores persona generation data from onboarding step 4';
COMMENT ON COLUMN persona_data.core_persona IS 'Core persona data (demographics, psychographics, etc.)';
COMMENT ON COLUMN persona_data.platform_personas IS 'Platform-specific personas (LinkedIn, Twitter, etc.)';
COMMENT ON COLUMN persona_data.quality_metrics IS 'Quality assessment metrics';
COMMENT ON COLUMN persona_data.selected_platforms IS 'Array of selected platforms';
