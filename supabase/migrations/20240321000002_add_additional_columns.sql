-- Add additional columns to founder_inputs table
ALTER TABLE founder_inputs 
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