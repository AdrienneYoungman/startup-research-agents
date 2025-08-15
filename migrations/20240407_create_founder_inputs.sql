-- Create founder_inputs table
CREATE TABLE IF NOT EXISTS public.founder_inputs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    founder_email TEXT NOT NULL,
    inputs JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (founder_email) REFERENCES public.founders(email)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_founder_inputs_email ON public.founder_inputs(founder_email);

-- Add RLS policies
ALTER TABLE public.founder_inputs ENABLE ROW LEVEL SECURITY;

-- Policy to allow founders to see their own inputs
CREATE POLICY "Founders can view their own inputs"
    ON public.founder_inputs
    FOR SELECT
    USING (founder_email = auth.jwt() ->> 'email');

-- Policy to allow founders to insert their own inputs
CREATE POLICY "Founders can insert their own inputs"
    ON public.founder_inputs
    FOR INSERT
    WITH CHECK (founder_email = auth.jwt() ->> 'email'); 