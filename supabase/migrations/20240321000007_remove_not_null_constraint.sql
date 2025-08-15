-- Remove NOT NULL constraint from inputs column in founder_inputs table
ALTER TABLE founder_inputs 
ALTER COLUMN inputs DROP NOT NULL;

-- Refresh schema cache
NOTIFY pgrst, 'reload schema';

-- Verify table structure
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'founder_inputs'; 