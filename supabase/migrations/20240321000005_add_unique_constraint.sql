-- Add unique constraint to founder_email in founder_inputs table
ALTER TABLE founder_inputs 
ADD CONSTRAINT unique_founder_email UNIQUE (founder_email);

-- Refresh schema cache
NOTIFY pgrst, 'reload schema';

-- Verify table structure
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'founder_inputs'; 