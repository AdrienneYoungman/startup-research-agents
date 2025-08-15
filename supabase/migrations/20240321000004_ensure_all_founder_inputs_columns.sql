-- Ensure all required columns exist in founder_inputs table
ALTER TABLE founder_inputs 
ADD COLUMN IF NOT EXISTS problem_domain TEXT,
ADD COLUMN IF NOT EXISTS problems TEXT[],
ADD COLUMN IF NOT EXISTS value_prop TEXT,
ADD COLUMN IF NOT EXISTS target_action TEXT,
ADD COLUMN IF NOT EXISTS follow_up_action TEXT,
ADD COLUMN IF NOT EXISTS is_paid_service BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS pricing_model TEXT,
ADD COLUMN IF NOT EXISTS price_points DECIMAL[],
ADD COLUMN IF NOT EXISTS pricing_questions TEXT[],
ADD COLUMN IF NOT EXISTS responses JSONB,
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS summary TEXT,
ADD COLUMN IF NOT EXISTS resonance_scores JSONB,
ADD COLUMN IF NOT EXISTS interview_version TEXT;

-- Refresh schema cache
NOTIFY pgrst, 'reload schema';

-- Verify table structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'founder_inputs'; 