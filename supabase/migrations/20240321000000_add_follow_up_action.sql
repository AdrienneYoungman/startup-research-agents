-- Ensure follow_up_action column exists
ALTER TABLE founder_inputs 
ADD COLUMN IF NOT EXISTS follow_up_action TEXT;

-- Refresh schema cache
NOTIFY pgrst, 'reload schema'; 