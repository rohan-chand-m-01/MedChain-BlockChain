-- Add patient names table for better UX
-- This allows doctors to see patient names instead of just wallet addresses

CREATE TABLE IF NOT EXISTS patient_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_wallet TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    date_of_birth DATE,
    phone TEXT,
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_patient_profiles_wallet ON patient_profiles(patient_wallet);

-- RLS policies
ALTER TABLE patient_profiles ENABLE ROW LEVEL SECURITY;

-- Patients can read/update their own profile
CREATE POLICY patient_profiles_patient_access ON patient_profiles
    FOR ALL
    USING (patient_wallet = current_setting('request.jwt.claims', true)::json->>'sub');

-- Doctors can read profiles of patients who granted them access
CREATE POLICY patient_profiles_doctor_access ON patient_profiles
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM access_grants
            WHERE access_grants.patient_wallet = patient_profiles.patient_wallet
            AND access_grants.doctor_wallet = current_setting('request.jwt.claims', true)::json->>'sub'
            AND access_grants.is_active = true
        )
    );

-- Function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_patient_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER patient_profiles_updated_at
    BEFORE UPDATE ON patient_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_patient_profiles_updated_at();

COMMENT ON TABLE patient_profiles IS 'Patient demographic information for better doctor UX';
