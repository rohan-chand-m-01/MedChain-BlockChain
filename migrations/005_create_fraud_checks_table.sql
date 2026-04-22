-- Create fraud_checks table for storing fraud detection results
-- This table tracks fraud scores and flags for each medical report analysis

CREATE TABLE IF NOT EXISTS fraud_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    fraud_score INTEGER NOT NULL CHECK (fraud_score >= 0 AND fraud_score <= 100),
    is_suspicious BOOLEAN NOT NULL DEFAULT FALSE,
    flags JSONB DEFAULT '[]'::jsonb,
    confidence INTEGER NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_fraud_checks_analysis_id ON fraud_checks(analysis_id);
CREATE INDEX IF NOT EXISTS idx_fraud_checks_patient_id ON fraud_checks(patient_id);
CREATE INDEX IF NOT EXISTS idx_fraud_checks_is_suspicious ON fraud_checks(is_suspicious);
CREATE INDEX IF NOT EXISTS idx_fraud_checks_created_at ON fraud_checks(created_at DESC);

-- Add comment
COMMENT ON TABLE fraud_checks IS 'Fraud detection results for medical report analyses';
COMMENT ON COLUMN fraud_checks.fraud_score IS 'Fraud score 0-100 based on physiological impossibility rules';
COMMENT ON COLUMN fraud_checks.is_suspicious IS 'True if fraud_score >= 40 (threshold for manual review)';
COMMENT ON COLUMN fraud_checks.flags IS 'Array of fraud flags with type, severity, and description';
COMMENT ON COLUMN fraud_checks.confidence IS 'Confidence level 0-100 based on available historical data';
