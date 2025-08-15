-- Ensure all columns exist in founder_inputs table
ALTER TABLE founder_inputs 
ADD COLUMN IF NOT EXISTS follow_up_action TEXT,
ADD COLUMN IF NOT EXISTS is_paid_service BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS pricing_model TEXT,
ADD COLUMN IF NOT EXISTS price_points DECIMAL[],
ADD COLUMN IF NOT EXISTS pricing_questions TEXT[];

-- Force schema refresh
NOTIFY pgrst, 'reload schema';

-- Verify table structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'founder_inputs'; 