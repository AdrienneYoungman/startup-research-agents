-- Create founder_inputs table
CREATE TABLE IF NOT EXISTS founder_inputs (
    id SERIAL PRIMARY KEY,
    founder_email TEXT NOT NULL,
    problem_domain TEXT NOT NULL,
    problems TEXT[] NOT NULL,
    value_prop TEXT NOT NULL,
    target_action TEXT NOT NULL,
    follow_up_action TEXT,
    is_paid_service BOOLEAN DEFAULT FALSE,
    pricing_model TEXT,
    price_points DECIMAL[],
    pricing_questions TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL UNIQUE,
    founder_email TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create responses table
CREATE TABLE IF NOT EXISTS responses (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    response_type TEXT NOT NULL,
    response_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Create index on founder_email for faster lookups
CREATE INDEX IF NOT EXISTS idx_founder_inputs_email ON founder_inputs(founder_email);

-- Create index on session_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_sessions_id ON sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_responses_session_id ON responses(session_id);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_founder_inputs_updated_at
    BEFORE UPDATE ON founder_inputs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 