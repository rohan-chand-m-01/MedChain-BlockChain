-- Add phone numbers and enhance profile management
-- This migration adds WhatsApp-compatible phone numbers for notifications

-- Add phone to patient_profiles if not exists
ALTER TABLE patient_profiles 
ADD COLUMN IF NOT EXISTS whatsapp_phone TEXT;

-- Create doctor_profiles table for web app doctors
CREATE TABLE IF NOT EXISTS doctor_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_wallet TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    specialty TEXT,
    whatsapp_phone TEXT,
    email TEXT,
    license_number TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_wallet ON doctor_profiles(doctor_wallet);
CREATE INDEX IF NOT EXISTS idx_patient_profiles_phone ON patient_profiles(whatsapp_phone);
CREATE INDEX IF NOT EXISTS idx_doctor_profiles_phone ON doctor_profiles(whatsapp_phone);

-- RLS policies for doctor_profiles
ALTER TABLE doctor_profiles ENABLE ROW LEVEL SECURITY;

-- Doctors can read/update their own profile
CREATE POLICY doctor_profiles_own_access ON doctor_profiles
    FOR ALL
    USING (doctor_wallet = current_setting('request.jwt.claims', true)::json->>'sub');

-- Patients can read doctor profiles (for selecting doctors)
CREATE POLICY doctor_profiles_public_read ON doctor_profiles
    FOR SELECT
    USING (true);

-- Function to auto-update doctor_profiles updated_at
CREATE OR REPLACE FUNCTION update_doctor_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER doctor_profiles_updated_at
    BEFORE UPDATE ON doctor_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_doctor_profiles_updated_at();

COMMENT ON TABLE doctor_profiles IS 'Doctor demographic information and contact details';
COMMENT ON COLUMN patient_profiles.whatsapp_phone IS 'WhatsApp number in format: whatsapp:+1234567890';
COMMENT ON COLUMN doctor_profiles.whatsapp_phone IS 'WhatsApp number in format: whatsapp:+1234567890';
