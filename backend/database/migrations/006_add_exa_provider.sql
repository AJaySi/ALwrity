-- Add EXA to subscription plans
ALTER TABLE subscription_plans 
ADD COLUMN exa_calls_limit INT DEFAULT 0;

-- Add EXA to usage summaries
ALTER TABLE usage_summaries 
ADD COLUMN exa_calls INT DEFAULT 0;

ALTER TABLE usage_summaries 
ADD COLUMN exa_cost FLOAT DEFAULT 0.0;

-- Update default limits for existing plans
UPDATE subscription_plans SET exa_calls_limit = 100 WHERE tier = 'free';
UPDATE subscription_plans SET exa_calls_limit = 500 WHERE tier = 'basic';
UPDATE subscription_plans SET exa_calls_limit = 2000 WHERE tier = 'pro';
UPDATE subscription_plans SET exa_calls_limit = 0 WHERE tier = 'enterprise';

