-- Ensure problem_domain column exists in founder_inputs table
ALTER TABLE founder_inputs 
ADD COLUMN IF NOT EXISTS problem_domain TEXT;

-- Refresh schema cache
NOTIFY pgrst, 'reload schema';

-- Verify table structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'founder_inputs'; 